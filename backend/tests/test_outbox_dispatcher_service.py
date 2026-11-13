from unittest.mock import MagicMock
from types import SimpleNamespace

import pytest

from app.services import outbox_dispatcher_service as dispatcher
from app.services import investigation_worker_service as investigation_worker


def test_publish_event_enqueues_the_investigation_task(monkeypatch):
    delay = MagicMock()
    monkeypatch.setattr(dispatcher.run_investigation_task, "delay", delay)

    dispatcher.publish_event(
        {
            "id": 1,
            "event_type": "INVESTIGATION_REQUESTED",
            "payload": {"investigation_id": 4},
        }
    )

    delay.assert_called_once_with(4)


def test_dispatch_marks_event_published_only_after_delay_returns(monkeypatch):
    claimed_event = {
        "id": 7,
        "event_type": "INVESTIGATION_REQUESTED",
        "payload": {"investigation_id": 4},
    }
    db = MagicMock()
    published = MagicMock()
    failed = MagicMock()

    monkeypatch.setattr(dispatcher, "SessionLocal", lambda: db)
    monkeypatch.setattr(dispatcher, "recover_stale_events", lambda _: 0)
    monkeypatch.setattr(dispatcher, "claim_pending_events", lambda *_args, **_kwargs: [claimed_event])
    monkeypatch.setattr(dispatcher, "mark_event_published", published)
    monkeypatch.setattr(dispatcher, "mark_event_failed", failed)
    monkeypatch.setattr(dispatcher, "publish_event", MagicMock())

    result = dispatcher.dispatch_pending_events()

    assert result["published_events"] == 1
    assert result["failed_events"] == 0
    published.assert_called_once_with(db=db, event_id=7)
    failed.assert_not_called()
    db.close.assert_called_once()


def test_dispatch_retains_event_and_logs_publish_exception(monkeypatch, caplog):
    claimed_event = {
        "id": 8,
        "event_type": "INVESTIGATION_REQUESTED",
        "payload": {"investigation_id": 4},
    }
    db = MagicMock()
    published = MagicMock()
    failed = MagicMock()

    monkeypatch.setattr(dispatcher, "SessionLocal", lambda: db)
    monkeypatch.setattr(dispatcher, "recover_stale_events", lambda _: 0)
    monkeypatch.setattr(dispatcher, "claim_pending_events", lambda *_args, **_kwargs: [claimed_event])
    monkeypatch.setattr(dispatcher, "mark_event_published", published)
    monkeypatch.setattr(dispatcher, "mark_event_failed", failed)
    monkeypatch.setattr(
        dispatcher,
        "publish_event",
        MagicMock(side_effect=ConnectionError("Redis unavailable")),
    )

    with caplog.at_level("ERROR"):
        result = dispatcher.dispatch_pending_events()

    assert result["published_events"] == 0
    assert result["failed_events"] == 1
    published.assert_not_called()
    failed.assert_called_once_with(db=db, event_id=8)
    assert "Redis unavailable" in caplog.text


def test_publish_event_rejects_missing_investigation_id():
    with pytest.raises(ValueError, match="no investigation_id"):
        dispatcher.publish_event(
            {
                "id": 9,
                "event_type": "INVESTIGATION_REQUESTED",
                "payload": {},
            }
        )


def test_duplicate_delivery_does_not_start_a_second_investigation(monkeypatch):
    db = MagicMock()
    investigation = SimpleNamespace(
        id=4,
        status="RUNNING",
        incident_id=19,
    )
    incident = SimpleNamespace(id=19)
    db.get.side_effect = [investigation, incident]
    claim = MagicMock(return_value=False)

    monkeypatch.setattr(investigation_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(investigation_worker, "claim_investigation", claim)

    result = investigation_worker.execute_investigation(4, "duplicate-task")

    assert result == {"investigation_id": 4, "status": "NOT_CLAIMED"}
    claim.assert_called_once_with(db, 4, "duplicate-task")
    db.close.assert_called_once()
