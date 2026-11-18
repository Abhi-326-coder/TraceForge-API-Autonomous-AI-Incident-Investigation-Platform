from datetime import datetime, timedelta, timezone
from uuid import UUID
from unittest.mock import MagicMock

import pytest

from app.db.models import Evidence, Investigation
from app.services.evidence_service import create_evidence
from app.services.evidence_service import find_evidence_by_source
from app.services.investigation_execution_context import (
    InvestigationExecution,
    bind_investigation_execution,
)
from app.graph import nodes


def _active_investigation(db_session, *, token=UUID(int=41), worker="worker-a"):
    investigation = Investigation(
        id=941,
        incident_id=777,
        status="RUNNING",
        worker_id=worker,
        lease_token=token,
        heartbeat_at=datetime.now(timezone.utc),
        lease_expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
    )
    db_session.add(investigation)
    db_session.commit()
    return InvestigationExecution(941, worker, token)


def _create(db_session, execution, source_reference, *, title="Summary", content="log result"):
    return create_evidence(
        db=db_session,
        investigation_id=941,
        source_type="LOG_ANALYSIS",
        provider="SIMULATOR",
        title=title,
        content=content,
        source_reference=source_reference,
        execution=execution,
    )


def test_evidence_write_survives_simulated_checkpoint_crash_and_retry(db_session):
    execution = _active_investigation(db_session)

    first = _create(db_session, execution, "checkout")
    # Simulate the node's DB commit succeeding before LangGraph checkpoint save.
    with pytest.raises(RuntimeError, match="simulated checkpoint failure"):
        raise RuntimeError("simulated checkpoint failure")
    retried = find_evidence_by_source(
        db_session,
        941,
        "LOG_ANALYSIS",
        "SIMULATOR",
        "checkout",
        execution,
    )

    assert retried.id == first.id
    assert retried.content == first.content
    assert db_session.query(Evidence).filter_by(investigation_id=941).count() == 1


def test_replayed_log_node_reuses_evidence_without_repeating_agent(monkeypatch, db_session):
    execution = _active_investigation(db_session)
    saved = _create(db_session, execution, "checkout", content="prior response")
    agent = MagicMock()
    monkeypatch.setattr(nodes, "GeminiLogAgent", agent)
    monkeypatch.setattr(nodes, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(nodes, "publish_event", MagicMock())

    with bind_investigation_execution(execution):
        result = nodes.log_investigation_node(
            {
                "investigation_id": 941,
                "incident": {"service": "checkout"},
            }
        )

    agent.assert_not_called()
    assert result["findings"][0]["summary"] == "prior response"
    assert result["findings"][0]["evidence_id"] == saved.id


def test_repeated_node_execution_deduplicates_only_same_explicit_source(db_session):
    execution = _active_investigation(db_session)

    first = _create(db_session, execution, "simulator://logs/checkout/10:00")
    repeated = _create(
        db_session,
        execution,
        "simulator://logs/checkout/10:00",
        title="A different label",
        content="different response text is not the identity",
    )
    distinct = _create(db_session, execution, "simulator://logs/checkout/10:01")

    assert repeated.id == first.id
    assert distinct.id != first.id
    assert db_session.query(Evidence).filter_by(investigation_id=941).count() == 2


def test_evidence_without_source_reference_is_not_arbitrarily_deduplicated(db_session):
    execution = _active_investigation(db_session)

    first = _create(db_session, execution, None)
    second = _create(db_session, execution, None)

    assert second.id != first.id


def test_lost_worker_lease_prevents_evidence_commit(db_session):
    old_execution = _active_investigation(db_session)
    investigation = db_session.get(Investigation, 941)
    investigation.worker_id = "worker-b"
    investigation.lease_token = UUID(int=42)
    investigation.lease_expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)
    db_session.commit()

    with pytest.raises(RuntimeError, match="lease is no longer owned"):
        _create(db_session, old_execution, "checkout")

    assert db_session.query(Evidence).filter_by(investigation_id=941).count() == 0
