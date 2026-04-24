from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import get_alert_service
from src.schemas import AlertItem
from src.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertItem])
async def list_alerts_view(
    service: Annotated[AlertService, Depends(get_alert_service)],
) -> list[AlertItem]:
    """Возвращает список всех алертов.

    Args:
        service: Экземпляр AlertService из dependency injection.

    Returns:
        Список AlertItem, отсортированный по дате (новые первые).
    """
    return await service.list_alerts()
