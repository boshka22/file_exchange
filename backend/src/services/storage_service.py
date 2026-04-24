import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from starlette import status

CHUNK_SIZE = 1024 * 1024  # 1 MB


class StorageService:
    def __init__(self, storage_dir: Path) -> None:
        self._storage_dir = storage_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, upload_file: UploadFile) -> tuple[str, str, str, int]:
        """Сохраняет загруженный файл на диск потоково.

        Args:
            upload_file: Загруженный файл из FastAPI.

        Returns:
            Кортеж (file_id, stored_name, mime_type, size_bytes).

        Raises:
            HTTPException 400: Если файл пустой.
        """
        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        stored_path = self._storage_dir / stored_name

        size = 0
        try:
            with stored_path.open("wb") as f:
                while chunk := await upload_file.read(CHUNK_SIZE):
                    f.write(chunk)
                    size += len(chunk)
        except Exception:
            stored_path.unlink(missing_ok=True)
            raise

        if size == 0:
            stored_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        mime_type = (
            upload_file.content_type
            or mimetypes.guess_type(stored_name)[0]
            or "application/octet-stream"
        )

        return file_id, stored_name, mime_type, size

    def get_path(self, stored_name: str) -> Path:
        """Возвращает абсолютный путь к файлу.

        Args:
            stored_name: Имя файла в хранилище.

        Returns:
            Абсолютный Path объект.
        """
        return self._storage_dir / stored_name

    def exists(self, stored_name: str) -> bool:
        """Проверяет существование файла на диске.

        Args:
            stored_name: Имя файла в хранилище.

        Returns:
            True если файл существует.
        """
        return (self._storage_dir / stored_name).exists()

    def delete(self, stored_name: str) -> None:
        """Удаляет файл с диска. Не падает, если файл уже удалён.

        Args:
            stored_name: Имя файла в хранилище.
        """
        (self._storage_dir / stored_name).unlink(missing_ok=True)
