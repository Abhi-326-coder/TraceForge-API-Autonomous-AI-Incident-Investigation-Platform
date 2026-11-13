import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.security import get_current_user
from app.services.authorization_service import get_owned_investigation
from app.tasks.investigation_tasks import run_investigation_task

router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigation Jobs"],
)
logger = logging.getLogger(__name__)


@router.post("/{investigation_id}/run", status_code=202)
def enqueue_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    investigation = get_owned_investigation(
        db,
        investigation_id,
        user,
    )

    if investigation.status != "QUEUED":
        raise HTTPException(
            status_code=409,
            detail="Investigation is not eligible to be queued.",
        )

    try:
        task = run_investigation_task.delay(
            investigation_id
        )

        return {
            "investigation_id": investigation_id,
            "task_id": task.id,
            "status": "QUEUED",
            "message": "Investigation queued for background execution.",
        }

    except Exception as exc:
        logger.exception(
            "Failed to queue investigation %s",
            investigation_id,
        )
        raise HTTPException(
            status_code=503,
            detail="Could not queue the investigation.",
        ) from exc
