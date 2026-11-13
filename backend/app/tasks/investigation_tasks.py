from app.db.database import SessionLocal
from langchain_google_genai.chat_models import (
    GoogleAuthenticationError,
    GoogleInvalidRequestError,
    GoogleModelNotFoundError,
    GooglePermissionDeniedError,
)

from app.services.investigation_state_service import (
    requeue_failed_investigation_for_retry,
)
from app.services.investigation_worker_service import (
    execute_investigation,
)
from app.worker import celery_app


@celery_app.task(
    bind=True,
    name="run_investigation_task",
    max_retries=2,
)
def run_investigation_task(
    self,
    investigation_id: int,
):
    try:
        if self.request.retries:
            db = SessionLocal()
            try:
                requeue_failed_investigation_for_retry(
                    db,
                    investigation_id,
                )
            finally:
                db.close()

        return execute_investigation(
            investigation_id=investigation_id,
            worker_id=self.request.id,
        )

    except (
        GoogleAuthenticationError,
        GoogleInvalidRequestError,
        GoogleModelNotFoundError,
        GooglePermissionDeniedError,
    ) as exc:
        raise RuntimeError(
            "Permanent Gemini API error. Verify GEMINI_API_KEY in "
            "Google AI Studio and confirm GEMINI_MODEL is available "
            "for this key. This task will not be retried automatically."
        ) from exc

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=10,
        )
