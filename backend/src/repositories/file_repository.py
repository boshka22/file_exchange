from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[StoredFile]:
        """Возвращает все файлы, отсортированные по дате создания (новые первые).

        Returns:
            Список ORM-объектов StoredFile.
        """
        result = await self._session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, file_id: str) -> StoredFile | None:
        """Возвращает файл по первичному ключу или None.

        Args:
            file_id: UUID файла.

        Returns:
            StoredFile или None если не найден.
        """
        return await self._session.get(StoredFile, file_id)

    async def create(self, file_item: StoredFile) -> StoredFile:
        """Добавляет новый файл в сессию и возвращает обновлённый объект.

        Args:
            file_item: Несохранённый ORM-объект.

        Returns:
            Объект с заполненными server_default полями.
        """
        self._session.add(file_item)
        await self._session.flush()
        await self._session.refresh(file_item)
        return file_item

    async def update(self, file_item: StoredFile) -> StoredFile:
        """Синхронизирует изменения ORM-объекта с БД.

        Args:
            file_item: Изменённый ORM-объект.

        Returns:
            Обновлённый объект с актуальными данными из БД.
        """
        await self._session.flush()
        await self._session.refresh(file_item)
        return file_item

    async def delete(self, file_item: StoredFile) -> None:
        """Удаляет файл из БД.

        Args:
            file_item: Объект для удаления.
        """
        await self._session.delete(file_item)
        await self._session.flush()
