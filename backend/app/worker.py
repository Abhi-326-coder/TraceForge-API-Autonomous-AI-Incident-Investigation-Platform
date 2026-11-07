from celery import Celery
from celery.schedules import crontab

from app.config import settings

# To start the celery worker :
# celery -A app.worker:celery_app worker --loglevel=info --pool=solo
# celery -A app.worker.celery_app beat --loglevel=info
celery_app = Celery(
    "traceforge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
    "app.tasks.investigation_tasks",
    "app.tasks.outbox_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=600,
    task_time_limit=660,

    beat_schedule={
        "dispatch-outbox-every-15-seconds": {
            "task": "dispatch_outbox_events",
            "schedule": 15.0,
        },
    },
)