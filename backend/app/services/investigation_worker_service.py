from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import (Investigation, Incident)
from app.graph.runtime import investigation_graph_runtime

def utc_now():
    return datetime.now(timezone.utc)


def build_initial_state(incident, investigation):
    """Create the initial state expected by InvestigationState."""
    return {
        "investigation_id": investigation.id,
        "incident": {
            "id": incident.id,
            "external_id": incident.external_id,
            "title": incident.title,
            "description": incident.description,
            "service": incident.service,
            "severity": incident.severity,
        },
        "evidence": [],
        "findings": [],
        "tool_calls": [],
        "investigation_plan": [],
        "next_agent": "",
        "investigation_complete": False,
        "final_finding": {},
    }


def execute_investigation(investigation_id: int) -> dict:
    db = SessionLocal()

    try:
        investigation = db.get(Investigation, investigation_id)

        if investigation is None:
            raise ValueError(
                f"Investigation {investigation_id} not found"
            )

        if investigation.status == "COMPLETED":
            return {
                "investigation_id": investigation_id,
                "status": "COMPLETED",
                "message": "Investigation already completed.",
            }

        incident = db.get(Incident, investigation.incident_id)

        if incident is None:
            raise ValueError(
                f"Incident for investigation {investigation_id} "
                "was not found"
            )

        investigation.status = "RUNNING"
        investigation.started_at = (
            investigation.started_at or utc_now()
        )
        db.commit()

        initial_state = build_initial_state(
            incident, investigation
        )

        # Reuse the same LangGraph checkpoint thread on retries.
        config = {
            "configurable": {
                "thread_id": f"investigation-{investigation_id}"
            }
        }

        with investigation_graph_runtime() as graph:
            snapshot = graph.get_state(config)

            if snapshot and snapshot.next:
                # A previous execution stopped mid-graph.
                result = graph.invoke(None, config=config)
            elif (
                snapshot
                and snapshot.values
                and snapshot.values.get("investigation_complete")
            ):
                # The graph may have finished before the database
                # status was updated.
                result = snapshot.values
            else:
                result = graph.invoke(
                    initial_state, config=config
                )

        investigation = db.get(
            Investigation, investigation_id
        )
        investigation.status = "COMPLETED"
        investigation.completed_at = utc_now()
        db.commit()

        return {
            "investigation_id": investigation_id,
            "status": "COMPLETED",
            "result": result,
        }

    except Exception:
        db.rollback()

        investigation = db.get(
            Investigation, investigation_id
        )

        if investigation is not None:
            investigation.status = "FAILED"
            investigation.completed_at = utc_now()
            db.commit()

        raise

    finally:
        db.close()
        
def run_graph_for_investigation(
    investigation_id: int,
    initial_state: dict,
):
    config = {
        "configurable": {
            "thread_id": f"investigation-{investigation_id}"
        }
    }

    with investigation_graph_runtime() as graph:
        result = graph.invoke(
            initial_state,
            config=config,
        )

    return result