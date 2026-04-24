from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_session
from src.services.alert_service import AlertService
from src.services.file_service import FileService
from src.services.storage_service import StorageService


@lru_cache
def get_storage_service() -> StorageService:
    """Создаёт синглтон StorageService.

    Returns:
        StorageService с директорией из настроек.
    """
    settings = get_settings()
    return StorageService(storage_dir=settings.storage_dir)


async def get_file_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> FileService:
    """Создаёт FileService для текущего запроса.

    Args:
        session: Сессия БД из get_session.
        storage: Синглтон StorageService из get_storage_service.

    Returns:
        FileService с внедрёнными зависимостями.
    """
    return FileService(session=session, storage=storage)


async def get_alert_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AlertService:
    """Создаёт AlertService для текущего запроса.

    Args:
        session: Сессия БД из get_session.

    Returns:
        AlertService с внедрённой сессией.
    """
    return AlertService(session=session)
