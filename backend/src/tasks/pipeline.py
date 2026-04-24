import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import get_settings
from src.models import StoredFile
from src.repositories.alert_repository import AlertRepository
from src.repositories.file_repository import FileRepository
from src.tasks.celery_app import celery_app

settings = get_settings()

SUSPICIOUS_EXTENSIONS: frozenset[str] = frozenset(
    {".exe", ".bat", ".cmd", ".sh", ".js", ".ps1", ".vbs", ".msi"}
)
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB


def detect_threats(file_item: StoredFile) -> list[str]:
    """Проверяет файл на признаки угроз.

    Args:
        file_item: Метаданные файла из БД.

    Returns:
        Список описаний найденных угроз. Пустой список — файл чистый.
    """
    reasons: list[str] = []
    extension = Path(file_item.original_name).suffix.lower()

    if extension in SUSPICIOUS_EXTENSIONS:
        reasons.append(f"suspicious extension: {extension}")

    if file_item.size > MAX_FILE_SIZE_BYTES:
        reasons.append(
            f"file size {file_item.size} bytes exceeds limit of {MAX_FILE_SIZE_BYTES}"
        )

    if extension == ".pdf" and file_item.mime_type not in {
        "application/pdf",
        "application/octet-stream",
    }:
        reasons.append(f"PDF extension does not match MIME type: {file_item.mime_type}")

    return reasons


def extract_metadata(file_item: StoredFile, stored_path: Path) -> dict:
    """Извлекает технические метаданные из файла.

    Args:
        file_item: Метаданные файла из БД.
        stored_path: Путь к файлу на диске.

    Returns:
        Словарь с техническими метаданными файла.
    """
    metadata: dict = {
        "extension": Path(file_item.original_name).suffix.lower(),
        "size_bytes": file_item.size,
        "mime_type": file_item.mime_type,
    }

    if file_item.mime_type.startswith("text/"):
        content = stored_path.read_text(encoding="utf-8", errors="ignore")
        metadata["line_count"] = len(content.splitlines())
        metadata["char_count"] = len(content)
    elif file_item.mime_type == "application/pdf":
        content = stored_path.read_bytes()
        metadata["approx_page_count"] = max(content.count(b"/Type /Page"), 1)

    return metadata


async def _run_pipeline(file_id: str) -> None:
    """Выполняет полный цикл обработки файла в одной DB-транзакции.

    NullPool используется намеренно: asyncio.run() создаёт новый event loop
    при каждом вызове задачи, а connection pool кэширует соединения под
    старый loop. NullPool отключает кэш — каждый вызов открывает свежее
    соединение и закрывает его после завершения.

    Args:
        file_id: UUID файла для обработки.
    """
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            file_repo = FileRepository(session)
            alert_repo = AlertRepository(session)

            file_item = await file_repo.get_by_id(file_id)
            if file_item is None:
                return

            file_item.processing_status = "processing"
            await session.flush()

            reasons = detect_threats(file_item)
            file_item.scan_status = "suspicious" if reasons else "clean"
            file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
            file_item.requires_attention = bool(reasons)

            stored_path = settings.storage_dir / file_item.stored_name
            if stored_path.exists():
                file_item.metadata_json = extract_metadata(file_item, stored_path)
                file_item.processing_status = "processed"
            else:
                file_item.processing_status = "failed"
                file_item.scan_status = "failed"
                file_item.scan_details = "stored file not found during metadata extraction"

            if file_item.processing_status == "failed":
                await alert_repo.create(
                    file_id=file_id,
                    level="critical",
                    message="File processing failed: stored file not found",
                )
            elif file_item.requires_attention:
                await alert_repo.create(
                    file_id=file_id,
                    level="warning",
                    message=f"File requires attention: {file_item.scan_details}",
                )
            else:
                await alert_repo.create(
                    file_id=file_id,
                    level="info",
                    message="File processed successfully",
                )

            await session.commit()
    finally:
        await engine.dispose()


@celery_app.task(name="process_file", bind=True, max_retries=3)
def process_file(self, file_id: str) -> None:
    """Celery-задача: запускает полный pipeline обработки файла.

    Args:
        file_id: UUID файла для обработки.
    """
    try:
        asyncio.run(_run_pipeline(file_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
