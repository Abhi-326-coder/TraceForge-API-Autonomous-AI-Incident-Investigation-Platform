from fastapi import APIRouter, HTTPException

from app.tasks.investigation_tasks import run_investigation_task

router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigation Jobs"],
)


@router.post("/{investigation_id}/run", status_code=202)
def enqueue_investigation(investigation_id: int):
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
        raise HTTPException(
            status_code=503,
            detail="Could not queue the investigation.",
        ) from exc