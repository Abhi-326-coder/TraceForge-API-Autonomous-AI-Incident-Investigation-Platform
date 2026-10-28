import pytest

from app.services.agent_metrics_service import AgentMetricsService


def test_records_agent_and_tool_metrics():
    service = AgentMetricsService()
    service.start_investigation(1)

    service.record_agent(
        1,
        agent_name="logs",
        status="SUCCESS",
        duration_ms=120,
    )
    service.record_tool(
        1,
        tool_name="search_logs",
        duration_ms=30,
        success=True,
    )

    report = service.get_report(1)

    assert report["agent_runs"] == 1
    assert report["tool_calls"] == 1
    assert report["tool_success_rate"] == 1.0
    assert report["agents"]["logs"]["successes"] == 1


def test_reports_failed_tools():
    service = AgentMetricsService()
    service.start_investigation(2)

    service.record_tool(
        2,
        tool_name="search_logs",
        duration_ms=20,
        success=False,
    )

    assert service.get_report(2)["tool_success_rate"] == 0.0


def test_approval_policy_is_reported():
    service = AgentMetricsService()
    service.start_investigation(3)

    service.record_approval_policy(
        3,
        approval_required=True,
        approval_observed=False,
    )

    assert service.get_report(3)["approval_policy_passed"] is False


def test_unknown_investigation_raises():
    service = AgentMetricsService()

    with pytest.raises(KeyError):
        service.get_report(999)