import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile
from src.repositories.alert_repository import AlertRepository
from src.repositories.file_repository import FileRepository


async def create_test_file(session: AsyncSession) -> StoredFile:
    file = StoredFile(
        id="alert-test-file",
        title="Test",
        original_name="test.txt",
        stored_name="alert-test-file.txt",
        mime_type="text/plain",
        size=100,
        processing_status="uploaded",
    )
    return await FileRepository(session).create(file)


@pytest.mark.asyncio
class TestAlertRepository:
    async def test_get_all_empty(self, session: AsyncSession):
        repo = AlertRepository(session)
        assert await repo.get_all() == []

    async def test_create_alert(self, session: AsyncSession):
        await create_test_file(session)
        repo = AlertRepository(session)

        alert = await repo.create(
            file_id="alert-test-file",
            level="info",
            message="Test alert message",
        )

        assert alert.id is not None
        assert alert.file_id == "alert-test-file"
        assert alert.level == "info"
        assert alert.message == "Test alert message"

    async def test_get_all_returns_all_alerts(self, session: AsyncSession):
        await create_test_file(session)
        repo = AlertRepository(session)

        await repo.create("alert-test-file", "info", "first")
        await repo.create("alert-test-file", "warning", "second")
        await repo.create("alert-test-file", "critical", "third")

        assert len(await repo.get_all()) == 3

    async def test_alerts_sorted_newest_first(self, session: AsyncSession):
        await create_test_file(session)
        repo = AlertRepository(session)

        await repo.create("alert-test-file", "info", "first alert")
        await repo.create("alert-test-file", "warning", "second alert")

        result = await repo.get_all()
        messages = [a.message for a in result]

        assert messages.index("second alert") < messages.index("first alert")
