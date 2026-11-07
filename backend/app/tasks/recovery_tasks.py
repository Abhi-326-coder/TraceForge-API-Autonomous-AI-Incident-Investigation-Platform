from celery import shared_task

from app.db.database import SessionLocal
from app.services.investigation_state_service import (
    recover_stale_investigations,
)
from app.tasks.investigation_tasks import (
    run_investigation_task,
)


@shared_task(name="recover_stale_investigations")
def recover_stale_investigation_jobs():

    db = SessionLocal()

    try:
        recovered_count = recover_stale_investigations(db)

        # The next scheduled recovery scan or an outbox-based
        # dispatcher should enqueue the recovered jobs.
        return {
            "recovered_count": recovered_count,
            "status": "RECOVERY_SCAN_COMPLETED",
        }

    finally:
        db.close()