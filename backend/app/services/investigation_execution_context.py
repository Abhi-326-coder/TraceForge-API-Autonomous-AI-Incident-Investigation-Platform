"""Per-process execution lease context; it is deliberately not checkpointed."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator
from uuid import UUID


@dataclass(frozen=True)
class InvestigationExecution:
    investigation_id: int
    worker_id: str
    lease_token: UUID


_current_execution: ContextVar[InvestigationExecution | None] = ContextVar(
    "traceforge_investigation_execution",
    default=None,
)


@contextmanager
def bind_investigation_execution(
    execution: InvestigationExecution,
) -> Iterator[None]:
    token = _current_execution.set(execution)
    try:
        yield
    finally:
        _current_execution.reset(token)


def current_investigation_execution() -> InvestigationExecution | None:
    return _current_execution.get()
