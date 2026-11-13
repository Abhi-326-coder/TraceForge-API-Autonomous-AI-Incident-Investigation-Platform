from datetime import datetime, timezone

from sqlalchemy.orm import Session
from opentelemetry import trace

from app.db.database import SessionLocal
from app.db.models import Incident, Investigation
from app.graph.runtime import investigation_graph_runtime
from app.observability.tracing import get_tracer

from app.services.investigation_state_service import (
    claim_investigation,
    complete_investigation,
    fail_investigation,
)

from app.services.worker_heartbeat_service import WorkerHeartbeat


tracer = get_tracer("traceforge.investigation")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_initial_state(
    incident: Incident,
    investigation: Investigation,
) -> dict:
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


def execute_investigation(
    investigation_id: int,
    worker_id: str,
) -> dict:
    db: Session = SessionLocal()

    try:
        with tracer.start_as_current_span(
            "investigation.execute"
        ) as span:

            span.set_attribute(
                "traceforge.investigation_id",
                investigation_id,
            )

            # 1. Load investigation.
            investigation = db.get(
                Investigation,
                investigation_id,
            )

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

            incident = db.get(
                Incident,
                investigation.incident_id,
            )

            if incident is None:
                raise ValueError(
                    "Incident associated with investigation not found"
                )

            # 2. Atomically claim the queued investigation.
            claimed = claim_investigation(
                db,
                investigation_id,
                worker_id,
            )

            if not claimed:
                return {
                    "investigation_id": investigation_id,
                    "status": "NOT_CLAIMED",
                }

            heartbeat = WorkerHeartbeat(
                investigation_id=investigation_id,
                worker_id=worker_id,
            )

            heartbeat.start()

            # 3. Prepare initial LangGraph state.
            initial_state = build_initial_state(
                incident,
                investigation,
            )

            config = {
                "configurable": {
                    "thread_id": f"investigation-{investigation_id}"
                }
            }

            # 4. Resume from checkpoint if one exists.
            with tracer.start_as_current_span(
                "investigation.langgraph"
            ) as graph_span:

                graph_span.set_attribute(
                    "traceforge.thread_id",
                    config["configurable"]["thread_id"],
                )

                with investigation_graph_runtime() as graph:

                    snapshot = graph.get_state(config)

                    if snapshot and snapshot.next:
                        result = graph.invoke(
                            None,
                            config=config,
                        )

                    elif (
                        snapshot
                        and snapshot.values
                        and snapshot.values.get(
                            "investigation_complete"
                        )
                    ):
                        result = snapshot.values

                    else:
                        result = graph.invoke(
                            initial_state,
                            config=config,
                        )

            # 5. Verify graph completion before marking completed.
            if not result.get("investigation_complete", False):
                raise RuntimeError(
                    "LangGraph finished without setting "
                    "investigation_complete=True."
                )
            
            if heartbeat.lost_lease.is_set():
                raise RuntimeError(
                    "Worker lost investigation lease."
                )

            completed = complete_investigation(
                db,
                investigation_id,
                worker_id,
            )

            if not completed:
                raise RuntimeError(
                    "Investigation ownership was lost before completion."
                )

            span.set_attribute(
                "traceforge.investigation.status",
                "COMPLETED",
            )

            return {
                "investigation_id": investigation_id,
                "status": "COMPLETED",
                "result": result,
            }

    except Exception as exc:
        db.rollback()

        try:
            fail_investigation(
                db,
                investigation_id,
                worker_id,
            )
        except Exception:
            db.rollback()

        current_span = trace.get_current_span()
        current_span.record_exception(exc)
        current_span.set_status(
            trace.Status(
                trace.StatusCode.ERROR,
                "Investigation execution failed",
            )
        )

        raise

    finally:
        if "heartbeat" in locals():
            heartbeat.stop()
        db.close()
