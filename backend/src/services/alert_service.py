from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert
from src.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AlertRepository(session)

    async def list_alerts(self) -> list[Alert]:
        """Возвращает все алерты.

        Returns:
            Список алертов, отсортированных по дате (новые первые).
        """
        return await self._repo.get_all()
