from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import AuditEvent, Incident, Investigation, OutboxEvent, Project, ProjectConnection, User
from app.services import outbox_dispatcher_service as dispatcher
from app.services.investigation_state_service import (
    claim_investigation, complete_investigation, fail_investigation,
    heartbeat_investigation, recover_stale_investigations,
)
from app.services import investigation_state_service as state_service
from app.tasks import recovery_tasks
from app.worker import celery_app


@pytest.fixture
def recovery_db():
    engine = create_engine("sqlite://")
    tables = [User.__table__, Project.__table__, Incident.__table__, Investigation.__table__,
              OutboxEvent.__table__, ProjectConnection.__table__, AuditEvent.__table__]
    Base.metadata.create_all(engine, tables=tables)
    db = sessionmaker(bind=engine)()
    try:
        user = User(email="recovery@example.com", password_hash="test")
        db.add(user); db.flush()
        project = Project(name="Recovery", owner_id=user.id); db.add(project); db.flush()
        incident = Incident(external_id="REC-1", title="Recovery", description="", service="api",
                            severity="LOW", status="OPEN", project_id=project.id)
        db.add(incident); db.flush()
        yield db, incident
    finally:
        db.close(); Base.metadata.drop_all(engine, tables=tables); engine.dispose()


def add_investigation(db, incident, status="RUNNING", lease=None, worker="worker-old", token=None):
    item = Investigation(incident_id=incident.id, status=status, current_stage="RUNNING",
                         worker_id=worker, lease_token=token,
                         heartbeat_at=lease, lease_expires_at=lease)
    db.add(item); db.commit(); db.refresh(item)
    return item


def add_dispatch_event(db, investigation, status="PUBLISHED"):
    event = OutboxEvent(event_type="INVESTIGATION_REQUESTED", aggregate_type="Investigation",
                        aggregate_id=str(investigation.id), idempotency_key=f"investigation-created-{investigation.id}",
                        payload={"investigation_id": investigation.id}, status=status,
                        attempts=1, published_at=datetime.now(timezone.utc) if status == "PUBLISHED" else None)
    db.add(event); db.commit(); db.refresh(event)
    return event


def test_recovery_task_is_registered_and_scheduled_with_outbox_dispatch():
    assert recovery_tasks.recover_stale_investigation_jobs.name == "recover_stale_investigations"
    assert recovery_tasks.recover_stale_investigation_jobs.app is celery_app
    schedule = celery_app.conf.beat_schedule
    assert schedule["dispatch-outbox-every-15-seconds"]["task"] == "dispatch_outbox_events"
    assert schedule["recover-stale-investigations-every-30-seconds"]["task"] == "recover_stale_investigations"
    assert "app.tasks.recovery_tasks" in celery_app.conf.include


def test_each_claim_gets_a_new_token_even_when_redelivery_reuses_task_id(recovery_db, monkeypatch):
    db, incident = recovery_db
    token_a, token_b = UUID(int=101), UUID(int=202)
    generated = iter((token_a, token_b))
    monkeypatch.setattr(state_service, "uuid4", lambda: next(generated))
    investigation = add_investigation(db, incident, status="QUEUED", lease=None, worker=None)
    first = claim_investigation(db, investigation.id, "same-celery-task-id")
    assert first == token_a

    investigation.lease_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    second = claim_investigation(db, investigation.id, "same-celery-task-id")
    assert second == token_b and second != first
    db.refresh(investigation)
    assert investigation.lease_token == token_b


def test_old_token_is_fenced_from_heartbeat_completion_and_failure(recovery_db, monkeypatch):
    db, incident = recovery_db
    token_a, token_b = UUID(int=301), UUID(int=302)
    generated = iter((token_a, token_b))
    monkeypatch.setattr(state_service, "uuid4", lambda: next(generated))
    investigation = add_investigation(db, incident, status="QUEUED", lease=None, worker=None)
    worker_id = "same-celery-task-id"
    assert claim_investigation(db, investigation.id, worker_id) == token_a
    investigation.lease_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    assert claim_investigation(db, investigation.id, worker_id) == token_b

    assert heartbeat_investigation(db, investigation.id, worker_id, token_a) is False
    assert complete_investigation(db, investigation.id, worker_id, token_a) is False
    assert fail_investigation(db, investigation.id, worker_id, token_a) is False
    db.refresh(investigation)
    assert investigation.status == "RUNNING" and investigation.lease_token == token_b
    assert heartbeat_investigation(db, investigation.id, worker_id, token_b) is True
    assert complete_investigation(db, investigation.id, worker_id, token_b) is True
    db.refresh(investigation)
    assert investigation.status == "COMPLETED" and investigation.lease_token is None


def test_current_token_can_fail_while_old_token_cannot(recovery_db):
    db, incident = recovery_db
    token = UUID(int=401)
    investigation = add_investigation(db, incident, status="RUNNING",
                                      lease=datetime.now(timezone.utc) + timedelta(minutes=1),
                                      worker="worker-current", token=token)
    assert fail_investigation(db, investigation.id, "worker-current", UUID(int=402)) is False
    assert fail_investigation(db, investigation.id, "worker-current", token) is True
    db.refresh(investigation)
    assert investigation.status == "FAILED" and investigation.lease_token is None


def test_expired_investigation_is_requeued_with_reused_durable_dispatch(recovery_db):
    db, incident = recovery_db
    expired = datetime.now(timezone.utc) - timedelta(minutes=5)
    previous_token = UUID(int=501)
    investigation = add_investigation(db, incident, lease=expired, token=previous_token)
    original_event = add_dispatch_event(db, investigation, status="PUBLISHED")

    assert recover_stale_investigations(db) == 1
    db.refresh(investigation); db.refresh(original_event)
    assert investigation.status == "QUEUED"
    assert investigation.worker_id is None and investigation.lease_expires_at is None
    assert investigation.lease_token is None
    assert original_event.status == "PENDING" and original_event.published_at is None
    assert db.query(OutboxEvent).filter_by(idempotency_key=f"investigation-created-{investigation.id}").count() == 1
    assert heartbeat_investigation(db, investigation.id, "worker-old", previous_token) is False
    assert complete_investigation(db, investigation.id, "worker-old", previous_token) is False
    assert fail_investigation(db, investigation.id, "worker-old", previous_token) is False

    assert recover_stale_investigations(db) == 0
    assert db.query(OutboxEvent).filter_by(aggregate_id=str(investigation.id)).count() == 1


def test_expired_legacy_investigation_gets_one_dispatch_event(recovery_db):
    db, incident = recovery_db
    investigation = add_investigation(db, incident, lease=datetime.now(timezone.utc) - timedelta(minutes=5))
    assert recover_stale_investigations(db) == 1
    assert recover_stale_investigations(db) == 0
    event = db.query(OutboxEvent).filter_by(idempotency_key=f"investigation-created-{investigation.id}").one()
    assert event.status == "PENDING"
    assert event.payload == {"investigation_id": investigation.id}


@pytest.mark.parametrize("missing_field", ["lease_expires_at", "lease_token", "worker_id", "heartbeat_at"])
def test_running_with_incomplete_lease_metadata_is_recovered(recovery_db, missing_field):
    db, incident = recovery_db
    future = datetime.now(timezone.utc) + timedelta(minutes=2)
    values = {"lease": future, "worker": "worker-present", "token": UUID(int=601)}
    investigation = add_investigation(db, incident, **values)
    if missing_field == "lease_expires_at":
        investigation.lease_expires_at = None
    elif missing_field == "lease_token":
        investigation.lease_token = None
    elif missing_field == "worker_id":
        investigation.worker_id = None
    else:
        investigation.heartbeat_at = None
    db.commit()

    assert recover_stale_investigations(db) == 1
    db.refresh(investigation)
    assert investigation.status == "QUEUED"
    assert investigation.worker_id is None and investigation.lease_token is None
    assert investigation.heartbeat_at is None and investigation.lease_expires_at is None
    assert db.query(OutboxEvent).filter_by(aggregate_id=str(investigation.id)).count() == 1


def test_queued_with_stale_lease_metadata_is_normalized_and_dispatched(recovery_db):
    db, incident = recovery_db
    investigation = add_investigation(
        db, incident, status="QUEUED", lease=datetime.now(timezone.utc) - timedelta(minutes=1),
        worker="stale-worker", token=UUID(int=701),
    )
    assert recover_stale_investigations(db) == 1
    db.refresh(investigation)
    assert investigation.status == "QUEUED"
    assert investigation.worker_id is None and investigation.lease_token is None
    assert investigation.heartbeat_at is None and investigation.lease_expires_at is None
    assert db.query(OutboxEvent).filter_by(aggregate_id=str(investigation.id)).one().status == "PENDING"


def test_completed_with_stale_lease_metadata_is_cleaned_but_never_requeued(recovery_db):
    db, incident = recovery_db
    investigation = add_investigation(
        db, incident, status="COMPLETED", lease=datetime.now(timezone.utc) - timedelta(minutes=1),
        worker="stale-worker", token=UUID(int=702),
    )
    assert recover_stale_investigations(db) == 1
    db.refresh(investigation)
    assert investigation.status == "COMPLETED"
    assert investigation.worker_id is None and investigation.lease_token is None
    assert investigation.heartbeat_at is None and investigation.lease_expires_at is None
    assert db.query(OutboxEvent).count() == 0


def test_failed_investigation_is_not_requeued_by_stale_recovery(recovery_db):
    db, incident = recovery_db
    investigation = add_investigation(
        db, incident, status="FAILED", lease=datetime.now(timezone.utc) - timedelta(minutes=1),
        worker="failed-worker", token=UUID(int=704),
    )
    assert recover_stale_investigations(db) == 0
    db.refresh(investigation)
    assert investigation.status == "FAILED"
    assert db.query(OutboxEvent).count() == 0


def test_recovery_claim_uses_skip_locked_for_competing_beat_runs():
    class EmptyResult:
        def scalars(self): return self
        def all(self): return []
    class Session:
        statement = None
        def execute(self, statement):
            self.statement = statement
            return EmptyResult()
        def commit(self): pass
        def rollback(self): pass
    session = Session()
    assert recover_stale_investigations(session) == 0
    assert session.statement._for_update_arg.skip_locked is True


def test_completed_and_active_investigations_are_not_recovered(recovery_db):
    db, incident = recovery_db
    active = datetime.now(timezone.utc) + timedelta(minutes=1)
    completed = add_investigation(db, incident, status="COMPLETED", lease=None, worker=None)
    running = add_investigation(db, incident, status="RUNNING", lease=active, worker="worker-active", token=UUID(int=703))
    assert recover_stale_investigations(db) == 0
    db.refresh(completed); db.refresh(running)
    assert completed.status == "COMPLETED"
    assert running.status == "RUNNING" and running.worker_id == "worker-active"
    assert db.query(OutboxEvent).count() == 0


def test_recovered_dispatch_is_published_by_existing_outbox_dispatcher(recovery_db, monkeypatch):
    db, incident = recovery_db
    investigation = add_investigation(db, incident, lease=datetime.now(timezone.utc) - timedelta(minutes=5))
    investigation_id = investigation.id
    add_dispatch_event(db, investigation, status="PUBLISHED")
    assert recover_stale_investigations(db) == 1
    calls = []
    monkeypatch.setattr(dispatcher, "SessionLocal", lambda: db)
    monkeypatch.setattr(dispatcher.run_investigation_task, "delay", lambda identifier: calls.append(identifier))

    result = dispatcher.dispatch_pending_events()
    assert result["published_events"] == 1
    assert calls == [investigation_id]
    event = db.query(OutboxEvent).filter_by(aggregate_id=str(investigation_id)).one()
    assert event.status == "PUBLISHED"


def test_recovery_and_dispatch_intent_roll_back_together(recovery_db, monkeypatch):
    db, incident = recovery_db
    old_token = UUID(int=705)
    investigation = add_investigation(db, incident, lease=datetime.now(timezone.utc) - timedelta(minutes=5), token=old_token)
    from app.services import investigation_state_service as state_service
    monkeypatch.setattr(state_service, "create_outbox_event", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("insert failed")))
    with pytest.raises(RuntimeError, match="insert failed"):
        recover_stale_investigations(db)
    db.refresh(investigation)
    assert investigation.status == "RUNNING" and investigation.lease_token == old_token
    assert db.query(OutboxEvent).count() == 0
