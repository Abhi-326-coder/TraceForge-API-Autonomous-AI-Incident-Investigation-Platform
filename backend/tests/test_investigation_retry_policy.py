from unittest.mock import MagicMock
from uuid import UUID

import httpx
import pytest
from celery.exceptions import Retry
from langchain_google_genai.chat_models import (
    GoogleAuthenticationError,
    GoogleInvalidRequestError,
)
from redis.exceptions import ConnectionError as RedisConnectionError

from app.services.investigation_retry import classify_investigation_failure
from app.services.investigation_state_service import (
    fail_investigation,
    requeue_failed_investigation_for_retry,
)
from app.db.models import Investigation
from app.llm import gemini
from app.tasks import investigation_tasks
from app.tasks.investigation_tasks import run_investigation_task


class ProviderStatusError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (ProviderStatusError(503, "private prompt"), "PROVIDER_UNAVAILABLE"),
        (ProviderStatusError(429, "credential-like detail"), "PROVIDER_RATE_LIMITED"),
        (httpx.ReadTimeout("private request"), "PROVIDER_TIMEOUT"),
        (ConnectionError("private endpoint"), "PROVIDER_CONNECTION"),
        (RedisConnectionError("redis endpoint detail"), "PROVIDER_CONNECTION"),
    ],
)
def test_transient_provider_errors_are_classified(error, category):
    result = classify_investigation_failure(error)

    assert result.retryable is True
    assert result.category == category
    assert "private" not in result.message
    assert "credential-like" not in result.message


@pytest.mark.parametrize(
    "error",
    [
        GoogleAuthenticationError("secret API key detail"),
        GoogleInvalidRequestError("private prompt detail"),
        ValueError("invalid investigation input"),
        NotImplementedError("unsupported provider operation"),
        RuntimeError("programming defect with source data"),
    ],
)
def test_permanent_and_unknown_errors_are_not_retryable(error):
    result = classify_investigation_failure(error)

    assert result.retryable is False
    assert str(error) not in result.message
    assert "secret API key" not in result.message


@pytest.mark.parametrize(
    "error",
    [
        ProviderStatusError(503, "provider body includes private prompt"),
        ProviderStatusError(429, "rate limit response includes credential"),
        httpx.ReadTimeout("request contains source content"),
    ],
)
def test_task_retries_transient_errors_with_safe_exponential_delay(
    monkeypatch,
    error,
):
    monkeypatch.setattr(
        investigation_tasks,
        "execute_investigation",
        MagicMock(side_effect=error),
    )
    retry = MagicMock(side_effect=Retry())
    monkeypatch.setattr(run_investigation_task, "retry", retry)
    monkeypatch.setattr(investigation_tasks.random, "uniform", lambda low, high: high)

    run_investigation_task.push_request(id="same-task-id", retries=0)
    try:
        with pytest.raises(Retry):
            run_investigation_task.run(23)
    finally:
        run_investigation_task.pop_request()

    retry.assert_called_once()
    kwargs = retry.call_args.kwargs
    assert kwargs["countdown"] == 10
    assert kwargs["max_retries"] == 2
    assert str(error) not in str(kwargs["exc"])


@pytest.mark.parametrize(
    "error",
    [
        GoogleAuthenticationError("secret key material"),
        GoogleInvalidRequestError("prompt body"),
        RuntimeError("source code and prompt"),
    ],
)
def test_permanent_and_unknown_task_errors_do_not_retry(monkeypatch, error):
    retry = MagicMock()
    monkeypatch.setattr(
        investigation_tasks,
        "execute_investigation",
        MagicMock(side_effect=error),
    )
    monkeypatch.setattr(run_investigation_task, "retry", retry)

    with pytest.raises(RuntimeError) as exc_info:
        run_investigation_task.run(23)

    retry.assert_not_called()
    assert str(error) not in str(exc_info.value)


def test_retry_exhaustion_is_terminal_and_sanitized(monkeypatch):
    error = ProviderStatusError(503, "secret and prompt must not escape")
    retry = MagicMock()
    monkeypatch.setattr(
        investigation_tasks,
        "execute_investigation",
        MagicMock(side_effect=error),
    )
    retry_db = MagicMock()
    monkeypatch.setattr(
        investigation_tasks,
        "SessionLocal",
        MagicMock(return_value=retry_db),
    )
    monkeypatch.setattr(
        investigation_tasks,
        "requeue_failed_investigation_for_retry",
        MagicMock(),
    )
    monkeypatch.setattr(run_investigation_task, "retry", retry)
    run_investigation_task.push_request(id="task", retries=2)
    try:
        with pytest.raises(RuntimeError, match="temporarily unavailable") as exc_info:
            run_investigation_task.run(23)
    finally:
        run_investigation_task.pop_request()

    retry.assert_not_called()
    assert str(error) not in str(exc_info.value)


def test_backoff_is_exponential_capped_and_jittered(monkeypatch):
    monkeypatch.setattr(investigation_tasks.random, "uniform", lambda low, high: high)

    assert investigation_tasks.retry_delay_seconds(0) == 10
    assert investigation_tasks.retry_delay_seconds(1) == 20
    assert investigation_tasks.retry_delay_seconds(10) == 60


def test_gemini_sdk_internal_retries_are_disabled(monkeypatch):
    constructor = MagicMock(return_value=object())
    monkeypatch.setattr(gemini.genai, "Client", constructor)

    gemini.GeminiClient()

    options = constructor.call_args.kwargs["http_options"]
    assert options.retry_options.attempts == 1


def test_fenced_failure_transition_persists_only_safe_details():
    db = MagicMock()
    db.execute.return_value.rowcount = 1
    token = UUID(int=17)

    assert fail_investigation(
        db,
        23,
        "worker-a",
        token,
        failure_category="PROVIDER_UNAVAILABLE",
        failure_message="The AI provider is temporarily unavailable.",
        failure_is_terminal=True,
    ) is True

    statement = db.execute.call_args.args[0]
    values = {
        key.key: value.value
        for key, value in statement._values.items()
    }
    assert values["failure_category"] == "PROVIDER_UNAVAILABLE"
    assert values["failure_message"] == "The AI provider is temporarily unavailable."
    assert values["failure_is_terminal"] is True
    assert values["status"] == "FAILED"
    assert token in statement.compile().params.values()


def test_historical_failed_investigation_is_not_requeued(db_session):
    investigation = Investigation(
        id=923,
        incident_id=999,
        status="FAILED",
        failure_category=None,
        failure_message=None,
        failure_is_terminal=None,
    )
    db_session.add(investigation)
    db_session.commit()

    with pytest.raises(RuntimeError, match="Unable to requeue"):
        requeue_failed_investigation_for_retry(db_session, 923)

    db_session.refresh(investigation)
    assert investigation.status == "FAILED"
