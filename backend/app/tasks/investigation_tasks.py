import random

from app.db.database import SessionLocal
from app.services.investigation_retry import classify_investigation_failure
from app.services.investigation_state_service import (
    requeue_failed_investigation_for_retry,
)
from app.services.investigation_worker_service import execute_investigation
from app.worker import celery_app


MAX_INVESTIGATION_RETRIES = 2
BASE_RETRY_DELAY_SECONDS = 10
MAX_RETRY_DELAY_SECONDS = 60


def retry_delay_seconds(retries: int) -> int:
    """Exponential backoff with equal jitter, capped at one minute."""
    exponent = min(max(retries, 0), 10)
    ceiling = min(
        BASE_RETRY_DELAY_SECONDS * (2**exponent),
        MAX_RETRY_DELAY_SECONDS,
    )
    return max(1, round(random.uniform(ceiling / 2, ceiling)))


@celery_app.task(
    bind=True,
    name="run_investigation_task",
    max_retries=MAX_INVESTIGATION_RETRIES,
)
def run_investigation_task(self, investigation_id: int):
    retries_used = self.request.retries
    try:
        if retries_used:
            db = SessionLocal()
            try:
                requeue_failed_investigation_for_retry(db, investigation_id)
            finally:
                db.close()

        return execute_investigation(
            investigation_id=investigation_id,
            worker_id=self.request.id,
            final_attempt=retries_used >= MAX_INVESTIGATION_RETRIES,
        )
    except Exception as exc:
        failure = classify_investigation_failure(exc)

        if failure.retryable and retries_used < MAX_INVESTIGATION_RETRIES:
            # Pass Celery only a fixed safe message. The original exception
            # may contain provider response bodies or request data.
            safe_error = RuntimeError(failure.message)
            raise self.retry(
                exc=safe_error,
                countdown=retry_delay_seconds(retries_used),
                max_retries=MAX_INVESTIGATION_RETRIES,
            ) from None

        # The worker's token-fenced FAILED transition has already persisted
        # this category and its sanitized message. Never expose the provider
        # exception or retry an unknown/programming error.
        raise RuntimeError(failure.message) from None
