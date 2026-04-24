from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Открывает сессию на время запроса.

    Yields:
        AsyncSession: Открытая сессия SQLAlchemy.
    """
    async with AsyncSessionFactory() as session:
        yield session
