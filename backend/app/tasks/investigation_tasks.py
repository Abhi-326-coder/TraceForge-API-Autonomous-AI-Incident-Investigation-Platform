from celery import shared_task

from app.services.investigation_worker_service import (
    execute_investigation,
)


@shared_task(
    bind=True,
    name="run_investigation_task",
    max_retries=2,
)
def run_investigation_task(
    self,
    investigation_id: int,
):
    try:
        return execute_investigation(
            investigation_id=investigation_id,
            worker_id=self.request.id,
        )

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=10,
        )