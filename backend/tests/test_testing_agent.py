from datetime import datetime, timezone

from app.agents.testing_agent import TestingAgent
from app.schemas.sandbox import SandboxResult


def make_result(
    status="PASSED",
    exit_code=0,
    timed_out=False,
    stderr="",
):
    now = datetime.now(timezone.utc)

    return SandboxResult(
        status=status,
        exit_code=exit_code,
        stdout="",
        stderr=stderr,
        duration_seconds=1.5,
        timed_out=timed_out,
        started_at=now,
        completed_at=now,
    )


def test_successful_exit_is_passed():
    report = TestingAgent().evaluate(make_result())

    assert report.status == "PASSED"


def test_nonzero_exit_is_failed():
    report = TestingAgent().evaluate(
        make_result(status="FAILED", exit_code=1)
    )

    assert report.status == "FAILED"


def test_timeout_is_inconclusive():
    report = TestingAgent().evaluate(
        make_result(
            status="TIMED_OUT",
            exit_code=None,
            timed_out=True,
        )
    )

    assert report.status == "INCONCLUSIVE"


def test_missing_dependency_is_inconclusive():
    report = TestingAgent().evaluate(
        make_result(
            status="FAILED",
            exit_code=1,
            stderr="ModuleNotFoundError: No module named 'pytest'",
        )
    )

    assert report.status == "INCONCLUSIVE"