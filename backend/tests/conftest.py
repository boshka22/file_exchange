import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app import app
from src.database import get_session
from src.dependencies import get_storage_service
from src.models import Base
from src.services.storage_service import StorageService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """Свежая in-memory БД для каждого теста — полная изоляция."""
    test_engine = create_async_engine(TEST_DATABASE_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def client(engine, tmp_path) -> AsyncClient:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session():
        async with session_factory() as s:
            yield s

    test_storage = StorageService(storage_dir=tmp_path)

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = lambda: test_storage

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
