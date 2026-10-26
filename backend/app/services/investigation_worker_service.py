
from datetime import datetime, timezone

from opentelemetry import trace
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Incident, Investigation
from app.graph.runtime import investigation_graph_runtime
from app.observability.tracing import get_tracer


tracer = get_tracer("traceforge.investigation")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_initial_state(
    incident: Incident,
    investigation: Investigation,
) -> dict:
    """Build the initial state expected by InvestigationState."""

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
    """
    Execute or recover an investigation using its stable LangGraph
    checkpoint thread.

    Celery can retry this function after a failure. Graph nodes and
    external side effects must still be idempotent.
    """

    db: Session = SessionLocal()

    try:
        with tracer.start_as_current_span(
            "investigation.execute"
        ) as span:
            span.set_attribute(
                "traceforge.investigation_id",
                investigation_id,
            )

            investigation = db.get(
                Investigation,
                investigation_id,
            )

            if investigation is None:
                raise ValueError(
                    f"Investigation {investigation_id} not found"
                )

            if investigation.status == "COMPLETED":
                span.set_attribute(
                    "traceforge.investigation.status",
                    "COMPLETED",
                )
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
                    f"Incident for investigation "
                    f"{investigation_id} not found"
                )

            # Persist RUNNING before starting graph execution.
            investigation.status = "RUNNING"
            investigation.started_at = (
                investigation.started_at or utc_now()
            )
            db.commit()

            initial_state = build_initial_state(
                incident,
                investigation,
            )

            # A stable thread ID is essential for checkpoint recovery.
            config = {
                "configurable": {
                    "thread_id": (
                        f"investigation-{investigation_id}"
                    )
                }
            }

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
                        # Resume a graph that has a pending node.
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
                        # Recover if the graph completed but the
                        # database status update did not.
                        result = snapshot.values

                    else:
                        result = graph.invoke(
                            initial_state,
                            config=config,
                        )

            # Refresh in case other code updated this row.
            investigation = db.get(
                Investigation,
                investigation_id,
            )

            if investigation is None:
                raise ValueError(
                    "Investigation disappeared during execution"
                )

            investigation.status = "COMPLETED"
            investigation.completed_at = utc_now()
            db.commit()

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
            investigation = db.get(
                Investigation,
                investigation_id,
            )

            if investigation is not None:
                investigation.status = "FAILED"
                investigation.completed_at = utc_now()
                db.commit()

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
        db.close()
