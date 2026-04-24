from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models import Alert, StoredFile
from src.repositories.alert_repository import AlertRepository
from src.repositories.file_repository import FileRepository
from src.services.storage_service import StorageService


class FileService:
    def __init__(self, session: AsyncSession, storage: StorageService) -> None:
        self._repo = FileRepository(session)
        self._storage = storage
        self._session = session

    async def list_files(self) -> list[StoredFile]:
        """Возвращает все загруженные файлы.

        Returns:
            Список файлов, отсортированных по дате создания (новые первые).
        """
        return await self._repo.get_all()

    async def get_file(self, file_id: str) -> StoredFile:
        """Возвращает файл по ID или бросает 404.

        Args:
            file_id: UUID файла.

        Returns:
            ORM-объект StoredFile.

        Raises:
            HTTPException 404: Если файл не найден.
        """
        file_item = await self._repo.get_by_id(file_id)
        if file_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return file_item

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        """Сохраняет файл на диск и создаёт запись в БД.

        Args:
            title: Пользовательское название файла.
            upload_file: Загруженный файл из HTTP-запроса.

        Returns:
            Созданный ORM-объект StoredFile.
        """
        file_id, stored_name, mime_type, size = await self._storage.save(upload_file)

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size=size,
            processing_status="uploaded",
        )
        result = await self._repo.create(file_item)
        await self._session.commit()
        return result

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        """Обновляет название файла.

        Args:
            file_id: UUID файла.
            title: Новое название.

        Returns:
            Обновлённый ORM-объект StoredFile.

        Raises:
            HTTPException 404: Если файл не найден.
        """
        file_item = await self.get_file(file_id)
        file_item.title = title
        result = await self._repo.update(file_item)
        await self._session.commit()
        return result

    async def delete_file(self, file_id: str) -> None:
        """Удаляет файл с диска и из БД.

        Args:
            file_id: UUID файла.

        Raises:
            HTTPException 404: Если файл не найден.
        """
        file_item = await self.get_file(file_id)
        self._storage.delete(file_item.stored_name)
        await self._session.execute(delete(Alert).where(Alert.file_id == file_id))
        await self._repo.delete(file_item)
        await self._session.commit()

    async def get_download_path(self, file_id: str) -> tuple[StoredFile, Path]:
        """Возвращает метаданные файла и путь к нему на диске.

        Args:
            file_id: UUID файла.

        Returns:
            Кортеж (StoredFile, Path к файлу на диске).

        Raises:
            HTTPException 404: Если файл не найден в БД или на диске.
        """
        file_item = await self.get_file(file_id)
        if not self._storage.exists(file_item.stored_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stored file not found on disk",
            )
        return file_item, self._storage.get_path(file_item.stored_name)
