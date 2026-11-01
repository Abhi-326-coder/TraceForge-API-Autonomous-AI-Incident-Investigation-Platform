from unittest.mock import MagicMock

from app.services.investigation_lock_service import (
    InvestigationLockService,
)


def test_acquire_lock_success():
    service = InvestigationLockService()
    service.redis = MagicMock()

    service.redis.set.return_value = True

    result = service.acquire(
        investigation_id=1,
        task_id="task-123",
    )

    assert result is True
    service.redis.set.assert_called_once()


def test_acquire_lock_failure():
    service = InvestigationLockService()
    service.redis = MagicMock()

    service.redis.set.return_value = None

    result = service.acquire(
        investigation_id=1,
        task_id="task-456",
    )

    assert result is False


def test_release_lock():
    service = InvestigationLockService()
    service.redis = MagicMock()

    service.redis.eval.return_value = 1

    result = service.release(
        investigation_id=1,
        task_id="task-123",
    )

    assert result is True