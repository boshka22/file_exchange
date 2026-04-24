from celery import Celery

from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "file_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
    include=["src.tasks.pipeline"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)