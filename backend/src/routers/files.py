from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from src.dependencies import get_file_service
from src.schemas import FileItem, FileUpdate
from src.services.file_service import FileService
from src.tasks.pipeline import process_file

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("", response_model=list[FileItem])
async def list_files_view(
    service: Annotated[FileService, Depends(get_file_service)],
) -> list[FileItem]:
    """Возвращает список всех загруженных файлов.

    Args:
        service: Экземпляр FileService из dependency injection.

    Returns:
        Список FileItem, отсортированный по дате создания (новые первые).
    """
    return await service.list_files()


@router.post("", response_model=FileItem, status_code=status.HTTP_201_CREATED)
async def create_file_view(
    service: Annotated[FileService, Depends(get_file_service)],
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
) -> FileItem:
    """Загружает файл и ставит задачу фоновой обработки.

    Args:
        service: Экземпляр FileService из dependency injection.
        title: Пользовательское название файла (из form-data).
        file: Загружаемый файл (из form-data).

    Returns:
        FileItem со статусом processing_status="uploaded".
    """
    file_item = await service.create_file(title=title, upload_file=file)
    process_file.delay(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file_view(
    file_id: str,
    service: Annotated[FileService, Depends(get_file_service)],
) -> FileItem:
    """Возвращает метаданные файла по его идентификатору.

    Args:
        file_id: UUID файла.
        service: Экземпляр FileService из dependency injection.

    Returns:
        FileItem с актуальными метаданными и статусами.

    Raises:
        HTTPException 404: Если файл не найден.
    """
    return await service.get_file(file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    service: Annotated[FileService, Depends(get_file_service)],
) -> FileItem:
    """Обновляет пользовательское название файла.

    Args:
        file_id: UUID файла.
        payload: Тело запроса с новым названием.
        service: Экземпляр FileService из dependency injection.

    Returns:
        Обновлённый FileItem.

    Raises:
        HTTPException 404: Если файл не найден.
    """
    return await service.update_file(file_id=file_id, title=payload.title)


@router.get("/{file_id}/download", response_class=FileResponse)
async def download_file_view(
    file_id: str,
    service: Annotated[FileService, Depends(get_file_service)],
) -> FileResponse:
    """Возвращает файл для скачивания.

    Args:
        file_id: UUID файла.
        service: Экземпляр FileService из dependency injection.

    Returns:
        FileResponse со скачиваемым файлом.

    Raises:
        HTTPException 404: Если файл не найден в БД или на диске.
    """
    file_item, stored_path = await service.get_download_path(file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_view(
    file_id: str,
    service: Annotated[FileService, Depends(get_file_service)],
) -> None:
    """Удаляет файл с диска и из базы данных.

    Args:
        file_id: UUID файла.
        service: Экземпляр FileService из dependency injection.

    Raises:
        HTTPException 404: Если файл не найден.
    """
    await service.delete_file(file_id)
