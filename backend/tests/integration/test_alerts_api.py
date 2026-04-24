import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert, StoredFile
from src.repositories.alert_repository import AlertRepository
from src.repositories.file_repository import FileRepository


async def seed_file_and_alert(
    session: AsyncSession,
    level: str = "info",
    message: str = "test",
) -> Alert:
    file = StoredFile(
        id="seed-file-id",
        title="Seed",
        original_name="seed.txt",
        stored_name="seed-file-id.txt",
        mime_type="text/plain",
        size=100,
        processing_status="processed",
    )
    await FileRepository(session).create(file)
    alert = await AlertRepository(session).create("seed-file-id", level, message)
    return alert


@pytest.mark.asyncio
class TestAlertsAPI:
    async def test_list_alerts_empty(self, client: AsyncClient):
        response = await client.get("/alerts")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_alerts_returns_created(
        self, client: AsyncClient, session: AsyncSession
    ):
        await seed_file_and_alert(session, level="warning", message="test warning")

        response = await client.get("/alerts")
        assert response.status_code == 200
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["level"] == "warning"
        assert alerts[0]["message"] == "test warning"

    async def test_alert_has_required_fields(
        self, client: AsyncClient, session: AsyncSession
    ):
        await seed_file_and_alert(session)

        alert = (await client.get("/alerts")).json()[0]
        assert all(k in alert for k in ("id", "file_id", "level", "message", "created_at"))
