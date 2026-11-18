from app.db.database import SessionLocal
from app.services.investigation_state_service import (
    recover_stale_investigations,
)
from app.worker import celery_app


@celery_app.task(name="recover_stale_investigations")
def recover_stale_investigation_jobs():

    db = SessionLocal()

    try:
        recovered_count = recover_stale_investigations(db)

        return {
            "recovered_count": recovered_count,
            "status": "RECOVERY_SCAN_COMPLETED",
        }

    finally:
        db.close()
