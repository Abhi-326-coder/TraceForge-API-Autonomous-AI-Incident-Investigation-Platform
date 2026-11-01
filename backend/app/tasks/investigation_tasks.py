from celery import shared_task

from app.services.investigation_worker_service import (
    execute_investigation,
)
from app.services.investigation_lock_service import (
    investigation_lock_service,
)


@shared_task(
    bind=True,
    name="run_investigation_task",
    max_retries=2,
)
def run_investigation_task(self, investigation_id: int):

    task_id = self.request.id

    acquired = investigation_lock_service.acquire(
        investigation_id=investigation_id,
        task_id=task_id,
        ttl_seconds=900,
    )

    if not acquired:
        return {
            "investigation_id": investigation_id,
            "status": "ALREADY_RUNNING",
            "message": "Another worker owns this investigation.",
        }

    try:
        result = execute_investigation(investigation_id)

        return result

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)

    finally:
        investigation_lock_service.release(
            investigation_id=investigation_id,
            task_id=task_id,
        )