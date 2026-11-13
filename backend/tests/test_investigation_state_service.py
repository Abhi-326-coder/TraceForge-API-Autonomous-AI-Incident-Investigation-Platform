from unittest.mock import MagicMock

import pytest

from app.services.investigation_state_service import (
    claim_investigation,
    complete_investigation,
    fail_investigation,
    requeue_failed_investigation_for_retry,
)


def test_queued_investigation_can_be_claimed():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = claim_investigation(db, 10, "worker-1")

    assert result is True
    db.commit.assert_called_once()


def test_duplicate_task_cannot_claim_already_running_investigation():
    db = MagicMock()
    db.execute.return_value.rowcount = 0

    result = claim_investigation(db, 10, "worker-2")

    assert result is False


def test_completed_investigation_cannot_be_claimed():
    db = MagicMock()
    db.execute.return_value.rowcount = 0

    result = claim_investigation(db, 10, "worker-1")

    assert result is False


def test_expired_running_lease_can_be_reclaimed():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = claim_investigation(db, 10, "replacement-worker")

    assert result is True


def test_complete_investigation_success():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = complete_investigation(db, 10, "worker-1")

    assert result is True


def test_fail_investigation_success():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = fail_investigation(db, 10, "worker-1")

    assert result is True


def test_failed_investigation_is_requeued_for_task_retry():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    requeue_failed_investigation_for_retry(db, 10)

    db.commit.assert_called_once()


def test_retry_requeue_fails_when_investigation_is_not_failed():
    db = MagicMock()
    db.execute.return_value.rowcount = 0

    with pytest.raises(RuntimeError, match="Unable to requeue"):
        requeue_failed_investigation_for_retry(db, 10)

    db.rollback.assert_called_once()
