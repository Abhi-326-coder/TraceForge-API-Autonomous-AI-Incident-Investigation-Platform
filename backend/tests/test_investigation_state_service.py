from unittest.mock import MagicMock

from app.services.investigation_state_service import (
    claim_investigation,
    complete_investigation,
    fail_investigation,
)


def test_claim_investigation_success():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = claim_investigation(db, 10)

    assert result is True
    db.commit.assert_called_once()


def test_claim_investigation_already_running():
    db = MagicMock()
    db.execute.return_value.rowcount = 0

    result = claim_investigation(db, 10)

    assert result is False


def test_complete_investigation_success():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = complete_investigation(db, 10)

    assert result is True


def test_fail_investigation_success():
    db = MagicMock()
    db.execute.return_value.rowcount = 1

    result = fail_investigation(db, 10)

    assert result is True