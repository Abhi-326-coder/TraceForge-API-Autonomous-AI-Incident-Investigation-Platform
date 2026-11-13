from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from langchain_google_genai.chat_models import (
    GoogleAuthenticationError,
    GoogleInvalidRequestError,
    GoogleModelNotFoundError,
    GooglePermissionDeniedError,
)

from app.tasks import investigation_tasks
from app.routes import investigation_jobs
from app.tasks.investigation_tasks import run_investigation_task
from app.worker import celery_app


@pytest.mark.parametrize(
    "error_type",
    [
        GoogleAuthenticationError,
        GoogleInvalidRequestError,
        GoogleModelNotFoundError,
        GooglePermissionDeniedError,
    ],
)
def test_permanent_gemini_errors_are_not_retried(
    monkeypatch,
    error_type,
):
    monkeypatch.setattr(
        investigation_tasks,
        "execute_investigation",
        MagicMock(side_effect=error_type("Gemini request rejected")),
    )

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        run_investigation_task.run(4)


def test_celery_retry_requeues_failed_investigation(monkeypatch):
    db = MagicMock()
    requeue = MagicMock()
    execute = MagicMock(return_value={"status": "COMPLETED"})
    monkeypatch.setattr(
        investigation_tasks,
        "SessionLocal",
        MagicMock(return_value=db),
    )
    monkeypatch.setattr(
        investigation_tasks,
        "requeue_failed_investigation_for_retry",
        requeue,
    )
    monkeypatch.setattr(
        investigation_tasks,
        "execute_investigation",
        execute,
    )

    run_investigation_task.push_request(
        id="retry-task-id",
        retries=1,
    )
    try:
        result = run_investigation_task.run(4)
    finally:
        run_investigation_task.pop_request()

    assert result == {"status": "COMPLETED"}
    requeue.assert_called_once_with(db, 4)
    execute.assert_called_once_with(
        investigation_id=4,
        worker_id="retry-task-id",
    )
    db.close.assert_called_once()


def test_investigation_task_uses_configured_celery_app():
    assert run_investigation_task.app is celery_app


def test_enqueue_publishes_queued_owned_investigation(monkeypatch):
    investigation = SimpleNamespace(id=4, status="QUEUED")
    task = SimpleNamespace(id="celery-task-id")
    delay = MagicMock(return_value=task)

    monkeypatch.setattr(
        investigation_jobs,
        "get_owned_investigation",
        lambda *_: investigation,
    )
    monkeypatch.setattr(
        investigation_jobs.run_investigation_task,
        "delay",
        delay,
    )

    result = investigation_jobs.enqueue_investigation(
        4,
        db=MagicMock(),
        user=MagicMock(),
    )

    assert result["task_id"] == "celery-task-id"
    assert result["status"] == "QUEUED"
    delay.assert_called_once_with(4)


def test_enqueue_returns_503_and_logs_broker_failure(monkeypatch, caplog):
    monkeypatch.setattr(
        investigation_jobs,
        "get_owned_investigation",
        lambda *_: SimpleNamespace(id=4, status="QUEUED"),
    )
    monkeypatch.setattr(
        investigation_jobs.run_investigation_task,
        "delay",
        MagicMock(side_effect=ConnectionError("Redis unavailable")),
    )

    with caplog.at_level("ERROR"):
        with pytest.raises(HTTPException) as exc_info:
            investigation_jobs.enqueue_investigation(
                4,
                db=MagicMock(),
                user=MagicMock(),
            )

    assert exc_info.value.status_code == 503
    assert "Redis unavailable" in caplog.text


def test_enqueue_rejects_investigation_not_queued(monkeypatch):
    delay = MagicMock()
    monkeypatch.setattr(
        investigation_jobs,
        "get_owned_investigation",
        lambda *_: SimpleNamespace(id=4, status="INVESTIGATING"),
    )
    monkeypatch.setattr(
        investigation_jobs.run_investigation_task,
        "delay",
        delay,
    )

    with pytest.raises(HTTPException) as exc_info:
        investigation_jobs.enqueue_investigation(
            4,
            db=MagicMock(),
            user=MagicMock(),
        )

    assert exc_info.value.status_code == 409
    delay.assert_not_called()
