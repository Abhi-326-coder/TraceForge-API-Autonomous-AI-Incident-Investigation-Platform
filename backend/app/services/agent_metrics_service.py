from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from time import perf_counter
from typing import Any


@dataclass
class AgentMetric:
    agent_name: str
    status: str
    duration_ms: float
    error_type: str | None = None


@dataclass
class ToolMetric:
    tool_name: str
    duration_ms: float
    success: bool


@dataclass
class InvestigationMetrics:
    investigation_id: int
    started_at: float = field(default_factory=perf_counter)
    agent_runs: list[AgentMetric] = field(default_factory=list)
    tool_runs: list[ToolMetric] = field(default_factory=list)
    root_cause_grounded: bool | None = None
    approval_required: bool = False
    approval_observed: bool = True


class AgentMetricsService:
    """Collect lightweight, in-process metrics for development."""

    def __init__(self) -> None:
        self._investigations: dict[int, InvestigationMetrics] = {}
        self._lock = Lock()

    def start_investigation(self, investigation_id: int) -> None:
        with self._lock:
            self._investigations.setdefault(
                investigation_id,
                InvestigationMetrics(investigation_id=investigation_id),
            )

    def record_agent(
        self,
        investigation_id: int,
        *,
        agent_name: str,
        status: str,
        duration_ms: float,
        error_type: str | None = None,
    ) -> None:
        if status not in {"SUCCESS", "FAILURE", "SKIPPED"}:
            raise ValueError("Unsupported agent status")

        with self._lock:
            metrics = self._get(investigation_id)
            metrics.agent_runs.append(
                AgentMetric(
                    agent_name=agent_name,
                    status=status,
                    duration_ms=max(0.0, duration_ms),
                    error_type=error_type,
                )
            )

    def record_tool(
        self,
        investigation_id: int,
        *,
        tool_name: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        with self._lock:
            metrics = self._get(investigation_id)
            metrics.tool_runs.append(
                ToolMetric(
                    tool_name=tool_name,
                    duration_ms=max(0.0, duration_ms),
                    success=success,
                )
            )

    def record_root_cause_quality(
        self,
        investigation_id: int,
        *,
        grounded: bool,
    ) -> None:
        with self._lock:
            self._get(investigation_id).root_cause_grounded = grounded

    def record_approval_policy(
        self,
        investigation_id: int,
        *,
        approval_required: bool,
        approval_observed: bool,
    ) -> None:
        with self._lock:
            metrics = self._get(investigation_id)
            metrics.approval_required = approval_required
            metrics.approval_observed = approval_observed

    def get_report(self, investigation_id: int) -> dict[str, Any]:
        with self._lock:
            metrics = self._get(investigation_id)

            agent_runs = list(metrics.agent_runs)
            tool_runs = list(metrics.tool_runs)

            agent_summary = {}
            grouped_agents = defaultdict(list)

            for run in agent_runs:
                grouped_agents[run.agent_name].append(run)

            for name, runs in grouped_agents.items():
                agent_summary[name] = {
                    "runs": len(runs),
                    "successes": sum(
                        run.status == "SUCCESS" for run in runs
                    ),
                    "failures": sum(
                        run.status == "FAILURE" for run in runs
                    ),
                    "average_duration_ms": round(
                        sum(run.duration_ms for run in runs) / len(runs), 2
                    ),
                }

            total_duration_ms = (
                perf_counter() - metrics.started_at
            ) * 1000

            return {
                "investigation_id": investigation_id,
                "duration_ms": round(total_duration_ms, 2),
                "agent_runs": len(agent_runs),
                "tool_calls": len(tool_runs),
                "tool_success_rate": (
                    round(
                        sum(tool.success for tool in tool_runs)
                        / len(tool_runs),
                        4,
                    )
                    if tool_runs
                    else None
                ),
                "agents": agent_summary,
                "root_cause_grounded": metrics.root_cause_grounded,
                "approval_required": metrics.approval_required,
                "approval_policy_passed": (
                    not metrics.approval_required
                    or metrics.approval_observed
                ),
            }

    def _get(self, investigation_id: int) -> InvestigationMetrics:
        metrics = self._investigations.get(investigation_id)
        if metrics is None:
            raise KeyError(
                f"Metrics not initialized for investigation {investigation_id}"
            )
        return metrics


agent_metrics_service = AgentMetricsService()

# The report at the end might look like this:
# {
#   "investigation_id": 123,
#   "duration_ms": 4820.5,
#   "agent_runs": 3,
#   "tool_calls": 5,
#   "tool_success_rate": 1.0,
#   "agents": {
#     "logs": {
#       "runs": 1,
#       "successes": 1,
#       "failures": 0,
#       "average_duration_ms": 850.0
#     }
#   },
#   "root_cause_grounded": true,
#   "approval_required": true,
#   "approval_policy_passed": true
# }