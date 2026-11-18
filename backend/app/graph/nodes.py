
from datetime import datetime, timezone
import hashlib
import json

from app.agents.gemini_log_agent import GeminiLogAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.root_cause_agent import RootCauseAgent

from app.db.database import SessionLocal
from app.db.models import Evidence
from app.schemas.event import InvestigationEvent
from app.services.event_bus import event_service
from app.services.evidence_service import (
    create_evidence,
    find_evidence_by_source,
)
from app.services.investigation_execution_context import (
    current_investigation_execution,
)
from app.services.investigation_state_service import (
    require_active_investigation_lease,
)
from app.config import settings
from simulator.main import get_logs, get_metrics


def publish_event(
    investigation_id: int,
    event_type: str,
    message: str,
    agent: str | None = None,
    data: dict | None = None,
):
    event_id = hashlib.sha256(
        json.dumps(
            [investigation_id, agent, event_type],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    event = InvestigationEvent(
        event_type=event_type,
        investigation_id=investigation_id,
        message=message,
        agent=agent,
        data=data or {},
        timestamp=datetime.now(timezone.utc),
        event_id=event_id,
    )

    execution = current_investigation_execution()
    if execution is None or execution.investigation_id != investigation_id:
        raise RuntimeError("Investigation node has no active execution lease.")

    db = SessionLocal()
    try:
        require_active_investigation_lease(
            db,
            investigation_id,
            execution.worker_id,
            execution.lease_token,
        )
        # Hold the investigation row lock through event publication so stale
        # executions cannot publish after a replacement has claimed the row.
        event_service.publish(event)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def supervisor_node(state):
    investigation_id = state["investigation_id"]

    publish_event(
        investigation_id,
        "supervisor_started",
        "Supervisor started investigation planning.",
        "supervisor",
    )

    supervisor = SupervisorAgent()

    plan = supervisor.create_plan(
        incident=state["incident"]
    )

    publish_event(
        investigation_id,
        "supervisor_completed",
        "Supervisor created investigation plan.",
        "supervisor",
        {"plan": plan},
    )

    return {
        "investigation_plan": plan,
        "next_agent": plan[0] if plan else "root_cause",
        "investigation_complete": False,
    }


def log_investigation_node(state):
    investigation_id = state["investigation_id"]

    publish_event(
        investigation_id,
        "agent_started",
        "Log Agent started investigation.",
        "log_agent",
    )

    source_reference = state["incident"]["service"]
    execution = current_investigation_execution()
    db = SessionLocal()
    try:
        existing_evidence = find_evidence_by_source(
            db=db,
            investigation_id=investigation_id,
            source_type="LOG_ANALYSIS",
            provider="SIMULATOR",
            source_reference=source_reference,
            execution=execution,
        )
    finally:
        db.close()

    if existing_evidence is not None:
        # A prior node execution may have committed evidence and then failed
        # before its checkpoint. Reuse it without repeating the Gemini call.
        result = existing_evidence.content
        evidence_id = existing_evidence.id
    else:
        agent = GeminiLogAgent()
        result = agent.investigate(incident=state["incident"])

        # Save the agent's summary and revalidate the lease in the same
        # transaction as the evidence insert or idempotent reuse.
        db = SessionLocal()
        try:
            evidence = create_evidence(
                db=db,
                investigation_id=investigation_id,
                source_type="LOG_ANALYSIS",
                provider="SIMULATOR",
                title="Log Agent Investigation Summary",
                content=result,
                source_reference=source_reference,
                execution=execution,
            )
            evidence_id = evidence.id
        finally:
            db.close()

    publish_event(
        investigation_id,
        "evidence_collected",
        "Log investigation summary saved as evidence.",
        "log_agent",
        {"evidence_id": evidence_id},
    )

    publish_event(
        investigation_id,
        "agent_completed",
        "Log Agent completed investigation.",
        "log_agent",
    )

    return {
        "findings": [
            {
                "agent": "logs",
                "summary": result,
                "evidence_id": evidence_id,
            }
        ]
    }


def metrics_investigation_node(state):
    if settings.demo_mode:
        metrics = get_metrics(state["incident"]["service"])
        summary = "DEMO metrics: " + ", ".join(f"{key}={value}" for key, value in sorted(metrics.items()))
        db = SessionLocal()
        try:
            evidence = create_evidence(
                db=db, investigation_id=state["investigation_id"],
                source_type="METRICS", provider="SIMULATOR",
                title="Seeded service metrics", content=summary,
                source_reference=None, execution=current_investigation_execution(),
            )
        finally:
            db.close()
        publish_event(state["investigation_id"], "evidence_collected", "Seeded metrics saved as evidence.", "metrics_agent", {"evidence_id": evidence.id})
        return {"findings": [{"agent": "metrics", "summary": summary, "evidence_id": evidence.id}]}
    publish_event(
        state["investigation_id"],
        "agent_completed",
        "Metrics Agent is not implemented yet.",
        "metrics_agent",
    )

    return {
        "findings": [
            {
                "agent": "metrics",
                "status": "NOT_IMPLEMENTED",
            }
        ]
    }


def code_investigation_node(state):
    publish_event(
        state["investigation_id"],
        "agent_completed",
        "Code Agent is not implemented yet.",
        "code_agent",
    )

    return {
        "findings": [
            {
                "agent": "code",
                "status": "NOT_IMPLEMENTED",
            }
        ]
    }


def advance_investigation_node(state):
    plan = state.get("investigation_plan", [])
    current = state.get("next_agent")

    if current in plan:
        current_index = plan.index(current)
        next_index = current_index + 1

        if next_index < len(plan):
            return {
                "next_agent": plan[next_index],
            }

    # All planned agents have finished.
    return {
        "next_agent": "root_cause",
    }


def root_cause_node(state):
    investigation_id = state["investigation_id"]

    publish_event(
        investigation_id,
        "root_cause_started",
        "Root Cause Agent started analysis.",
        "root_cause_agent",
    )

    # Retrieve evidence saved for this investigation.
    db = SessionLocal()

    try:
        evidence_records = (
            db.query(Evidence)
            .filter(
                Evidence.investigation_id == investigation_id
            )
            .order_by(Evidence.id.asc())
            .all()
        )

        evidence = [
            {
                "id": item.id,
                "source_type": item.source_type,
                "provider": item.provider,
                "title": item.title,
                "content": item.content,
                "source_reference": item.source_reference,
            }
            for item in evidence_records
        ]

    finally:
        db.close()

    agent = RootCauseAgent()

    result = agent.analyze(
        evidence=evidence
    )

    final_finding = result.model_dump()

    db = SessionLocal()
    try:
        create_evidence(
            db=db, investigation_id=investigation_id,
        source_type="ROOT_CAUSE", provider="TRACEFORGE_DEMO" if settings.demo_mode else "TRACEFORGE",
            title="Root cause analysis", content=json.dumps(final_finding),
            source_reference=f"investigation:{investigation_id}:root-cause", execution=current_investigation_execution(),
        )
    finally:
        db.close()

    publish_event(
        investigation_id,
        "root_cause_completed",
        "Root Cause Agent completed analysis.",
        "root_cause_agent",
        {
            "root_cause": result.root_cause,
            "confidence": result.confidence,
        },
    )

    publish_event(
        investigation_id,
        "investigation_completed",
        "Investigation completed successfully.",
        "supervisor",
    )

    return {
        "final_finding": final_finding,
        "investigation_complete": True,
    }
