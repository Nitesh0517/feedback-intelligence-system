from celery import Celery
from app.core.config import settings

is_testing = settings.ENVIRONMENT == "testing" or getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False)

celery_app = Celery(
    "feedback_tasks",
    broker="memory://" if is_testing else settings.CELERY_BROKER_URL,
    backend="cache+memory://" if is_testing else settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.feedback_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=270,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    task_always_eager=is_testing,
    task_store_eager_result=is_testing,
)
