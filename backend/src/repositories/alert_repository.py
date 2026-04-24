from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Alert]:
        """Возвращает все алерты, отсортированные по дате (новые первые).

        Returns:
            Список ORM-объектов Alert.
        """
        result = await self._session.execute(
            select(Alert).order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, file_id: str, level: str, message: str) -> Alert:
        """Создаёт новый алерт в рамках текущей транзакции.

        Args:
            file_id: UUID файла, к которому относится алерт.
            level: Уровень серьёзности (info, warning, critical).
            message: Текст сообщения.

        Returns:
            Созданный объект Alert с заполненным id и created_at.
        """
        alert = Alert(file_id=file_id, level=level, message=message)
        self._session.add(alert)
        await self._session.flush()
        await self._session.refresh(alert)
        return alert
