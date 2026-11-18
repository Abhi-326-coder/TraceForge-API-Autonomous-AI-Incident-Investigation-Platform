from contextlib import nullcontext
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID

from app.services import investigation_worker_service as worker_service
from app.services.investigation_execution_context import (
    InvestigationExecution,
    current_investigation_execution,
)
from app.graph import runtime as graph_runtime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph


class FakeHeartbeat:
    def __init__(self, **_kwargs):
        self.lost_lease = Event()

    def start(self):
        pass

    def stop(self):
        pass


class FakeGraph:
    def __init__(self, snapshot, result=None):
        self.snapshot = snapshot
        self.result = result or {"investigation_complete": True}
        self.invoke_calls = []
        self.on_invoke = None

    def get_state(self, _config):
        return self.snapshot

    def invoke(self, input_value, *, config):
        self.invoke_calls.append((input_value, config))
        if self.on_invoke:
            self.on_invoke()
        return self.result


def _run_worker(monkeypatch, graph, *, investigation_status="QUEUED", lease_token=UUID(int=501)):
    db = MagicMock()
    incident = SimpleNamespace(
        id=73,
        external_id="INC-73",
        title="Checkout errors",
        description="Elevated errors",
        service="checkout",
        severity="high",
    )
    investigation = SimpleNamespace(
        id=41,
        incident_id=73,
        status=investigation_status,
    )
    db.get.side_effect = [investigation, incident]

    monkeypatch.setattr(worker_service, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        worker_service,
        "claim_investigation",
        MagicMock(return_value=lease_token),
    )
    complete = MagicMock(return_value=True)
    monkeypatch.setattr(worker_service, "complete_investigation", complete)
    monkeypatch.setattr(worker_service, "WorkerHeartbeat", FakeHeartbeat)
    monkeypatch.setattr(
        worker_service,
        "investigation_graph_runtime",
        lambda: nullcontext(graph),
    )
    return db, complete


def test_completed_checkpoint_repairs_stale_database_status(monkeypatch):
    checkpoint_values = {
        "investigation_id": 41,
        "investigation_complete": True,
        "final_finding": {"root_cause": "pool exhaustion"},
    }
    graph = FakeGraph(SimpleNamespace(next=("stale_pending_task",), values=checkpoint_values))
    db, complete = _run_worker(monkeypatch, graph)

    result = worker_service.execute_investigation(41, "worker-b")

    assert result["status"] == "COMPLETED"
    assert result["result"] is checkpoint_values
    assert graph.invoke_calls == []
    complete.assert_called_once_with(db, 41, "worker-b", UUID(int=501))


def test_incomplete_checkpoint_resumes_with_replacement_worker_lease(monkeypatch):
    graph = FakeGraph(SimpleNamespace(next=("logs",), values={"findings": []}))
    execution_seen = []
    graph.on_invoke = lambda: execution_seen.append(
        current_investigation_execution()
    )
    db, complete = _run_worker(
        monkeypatch,
        graph,
        investigation_status="QUEUED",
        lease_token=UUID(int=502),
    )

    result = worker_service.execute_investigation(41, "replacement-worker")

    assert result["status"] == "COMPLETED"
    assert graph.invoke_calls[0][0] is None
    assert execution_seen[0].worker_id == "replacement-worker"
    assert execution_seen[0].lease_token == UUID(int=502)
    complete.assert_called_once_with(db, 41, "replacement-worker", UUID(int=502))


def test_incomplete_checkpoint_without_pending_work_is_rejected(monkeypatch):
    graph = FakeGraph(SimpleNamespace(next=(), values={"findings": ["partial"]}))
    db, complete = _run_worker(monkeypatch, graph)

    try:
        worker_service.execute_investigation(41, "worker-a")
    except ValueError as exc:
        assert "no pending work" in str(exc)
    else:
        raise AssertionError("inconsistent checkpoint should fail")

    assert graph.invoke_calls == []
    complete.assert_not_called()
    # The worker's main session and the fenced stage-update session both close.
    assert db.close.call_count == 2


def test_empty_checkpoint_starts_new_graph_run(monkeypatch):
    graph = FakeGraph(None)
    _run_worker(monkeypatch, graph)

    result = worker_service.execute_investigation(41, "worker-a")

    assert result["status"] == "COMPLETED"
    assert graph.invoke_calls[0][0]["investigation_id"] == 41


def test_checkpoint_writes_hold_current_lease_fence(monkeypatch):
    db = MagicMock()
    delegate = MagicMock()
    delegate.serde = JsonPlusSerializer()
    execution = InvestigationExecution(41, "worker-b", UUID(int=503))
    require_lease = MagicMock()
    monkeypatch.setattr(graph_runtime, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        graph_runtime,
        "require_active_investigation_lease",
        require_lease,
    )
    fenced = graph_runtime.LeaseFencedCheckpointer(delegate, execution)

    result = fenced.put("config", "checkpoint", "metadata", "versions")

    assert result == delegate.put.return_value
    require_lease.assert_called_once_with(db, 41, "worker-b", UUID(int=503))
    delegate.put.assert_called_once()
    db.commit.assert_called_once()
    db.close.assert_called_once()


def test_stale_worker_cannot_write_checkpoint(monkeypatch):
    db = MagicMock()
    delegate = MagicMock()
    delegate.serde = JsonPlusSerializer()
    monkeypatch.setattr(graph_runtime, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        graph_runtime,
        "require_active_investigation_lease",
        MagicMock(side_effect=RuntimeError("lease lost")),
    )
    fenced = graph_runtime.LeaseFencedCheckpointer(
        delegate,
        InvestigationExecution(41, "old-worker", UUID(int=504)),
    )

    try:
        fenced.put("config", "checkpoint", "metadata", "versions")
    except RuntimeError as exc:
        assert "lease lost" in str(exc)
    else:
        raise AssertionError("stale worker checkpoint write should fail")

    delegate.put.assert_not_called()
    db.rollback.assert_called_once()
    db.close.assert_called_once()


def test_lease_fenced_checkpointer_implements_langgraph_protocol(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(graph_runtime, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        graph_runtime,
        "require_active_investigation_lease",
        MagicMock(),
    )
    delegate = InMemorySaver()
    checkpointer = graph_runtime.LeaseFencedCheckpointer(
        delegate,
        InvestigationExecution(41, "worker-c", UUID(int=505)),
    )
    builder = StateGraph(dict)
    builder.add_node("identity", lambda state: state)
    builder.add_edge(START, "identity")
    builder.add_edge("identity", END)
    graph = builder.compile(checkpointer=checkpointer)

    result = graph.invoke(
        {"value": 7},
        config={"configurable": {"thread_id": "fenced-protocol-test"}},
    )

    assert result == {"value": 7}
    assert db.commit.call_count >= 1
