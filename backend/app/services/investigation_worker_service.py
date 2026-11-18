from datetime import datetime, timezone
from uuid import UUID

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
from app.services.investigation_retry import classify_investigation_failure
from app.services.investigation_execution_context import (
    InvestigationExecution,
    bind_investigation_execution,
)

from app.services.worker_heartbeat_service import WorkerHeartbeat
from app.config import settings
from app.services.event_bus import event_service
from app.schemas.event import InvestigationEvent


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
    final_attempt: bool = False,
) -> dict:
    db: Session = SessionLocal()
    lease_token: UUID | None = None

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

            # 2. Atomically claim the queued investigation.
            lease_token = claim_investigation(
                db,
                investigation_id,
                worker_id,
            )

            if lease_token is None:
                return {
                    "investigation_id": investigation_id,
                    "status": "NOT_CLAIMED",
                }

            db.query(Investigation).filter(Investigation.id == investigation_id).update(
                {Investigation.current_stage: "RUNNING"}, synchronize_session=False
            )
            db.commit()

            event_service.publish(InvestigationEvent(
                event_type="investigation_started", investigation_id=investigation_id,
                message="Investigation execution started.", agent="supervisor",
                data={"mode": "DEMO" if settings.demo_mode else "LIVE"},
                timestamp=utc_now(), event_id=f"investigation-started-{investigation_id}",
            ))

            def update_stage(stage: str) -> None:
                stage_db = SessionLocal()
                try:
                    stage_db.query(Investigation).filter(
                        Investigation.id == investigation_id,
                        Investigation.status == "RUNNING",
                        Investigation.lease_token == lease_token,
                        Investigation.worker_id == worker_id,
                    ).update({Investigation.current_stage: stage}, synchronize_session=False)
                    stage_db.commit()
                finally:
                    stage_db.close()

            # Validate related input only after acquiring the lease so an
            # irrecoverable relationship failure can be persisted through the
            # same token-fenced failure transition as execution errors.
            incident = db.get(
                Incident,
                investigation.incident_id,
            )

            if incident is None:
                raise ValueError(
                    "Incident associated with investigation not found"
                )

            heartbeat = WorkerHeartbeat(
                investigation_id=investigation_id,
                worker_id=worker_id,
                lease_token=lease_token,
            )

            heartbeat.start()

            # Stage updates are delivered through graph events; the existing
            # outbox and status API remain authoritative for worker lifecycle.

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
            execution = InvestigationExecution(
                investigation_id=investigation_id,
                worker_id=worker_id,
                lease_token=lease_token,
            )
            with bind_investigation_execution(execution):
                with tracer.start_as_current_span(
                    "investigation.langgraph"
                ) as graph_span:

                    graph_span.set_attribute(
                        "traceforge.thread_id",
                        config["configurable"]["thread_id"],
                    )

                    update_stage("ANALYZING")

                    with investigation_graph_runtime() as graph:

                        snapshot = graph.get_state(config)

                        if (
                            snapshot
                            and snapshot.values
                            and snapshot.values.get("investigation_complete")
                        ):
                            result = snapshot.values

                        elif snapshot and snapshot.next:
                            result = graph.invoke(
                                None,
                                config=config,
                            )

                        elif snapshot and snapshot.values:
                            raise ValueError(
                                "Persisted investigation checkpoint has state "
                                "but no pending work or completion marker."
                            )
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

            update_stage("COMPLETING")
            
            if heartbeat.lost_lease.is_set():
                raise RuntimeError(
                    "Worker lost investigation lease."
                )

            completed = complete_investigation(
                db,
                investigation_id,
                worker_id,
                lease_token,
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
        failure = classify_investigation_failure(exc)

        if lease_token is not None:
            try:
                fail_investigation(
                    db,
                    investigation_id,
                    worker_id,
                    lease_token,
                    failure_category=failure.category,
                    failure_message=failure.message,
                    failure_is_terminal=(
                        not failure.retryable or final_attempt
                    ),
                )
            except Exception:
                db.rollback()

        current_span = trace.get_current_span()
        current_span.set_status(
            trace.Status(
                trace.StatusCode.ERROR,
                f"{failure.category}: {failure.message}",
            )
        )

        raise

    finally:
        if "heartbeat" in locals():
            heartbeat.stop()
        db.close()
