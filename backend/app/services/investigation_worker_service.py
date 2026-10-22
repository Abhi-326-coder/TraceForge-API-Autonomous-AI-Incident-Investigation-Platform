from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import Investigation


def execute_investigation(
    investigation_id: int,
) -> dict:
    db = SessionLocal()

    try:
        investigation = db.get(
            Investigation,
            investigation_id,
        )

        if investigation is None:
            raise ValueError(
                f"Investigation {investigation_id} not found"
            )

        # Prevent an ordinary duplicate task from starting a
        # completed investigation again.
        if investigation.status == "COMPLETED":
            return {
                "investigation_id": investigation_id,
                "status": "COMPLETED",
                "message": "Investigation already completed.",
            }

        investigation.status = "RUNNING"
        investigation.started_at = (
            investigation.started_at
            or datetime.now(timezone.utc)
        )
        db.commit()

        # IMPORTANT:
        # Connect your existing compiled LangGraph graph here.
        #
        # Use the actual graph object/function from your project.
        # Do not create a second graph just for Celery.
        #
        # Example integration shape:
        #
        # graph = get_compiled_investigation_graph()
        # result = graph.invoke(existing_initial_state)
        #
        # The initial state must include the fields required by
        # your current InvestigationState TypedDict.

        raise NotImplementedError(
            "Connect the existing LangGraph graph and initial "
            "state here before running background investigations."
        )

    except NotImplementedError:
        investigation = db.get(
            Investigation,
            investigation_id,
        )
        if investigation is not None:
            investigation.status = "FAILED"
            investigation.completed_at = datetime.now(
                timezone.utc
            )
            db.commit()
        raise

    except Exception:
        db.rollback()

        investigation = db.get(
            Investigation,
            investigation_id,
        )

        if investigation is not None:
            investigation.status = "FAILED"
            investigation.completed_at = datetime.now(
                timezone.utc
            )
            db.commit()

        raise

    finally:
        db.close()