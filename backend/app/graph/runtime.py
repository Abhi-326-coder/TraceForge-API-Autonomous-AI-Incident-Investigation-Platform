from contextlib import contextmanager

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.db.database import SessionLocal
from app.services.investigation_execution_context import (
    InvestigationExecution,
    current_investigation_execution,
)
from app.services.investigation_state_service import (
    require_active_investigation_lease,
)


class LeaseFencedCheckpointer(BaseCheckpointSaver):
    """Delegate checkpoint reads and fence every checkpoint write by lease."""

    def __init__(self, checkpointer, execution: InvestigationExecution):
        super().__init__(serde=checkpointer.serde)
        self._checkpointer = checkpointer
        self._execution = execution

    def __getattr__(self, name):
        return getattr(self._checkpointer, name)

    def get_tuple(self, *args, **kwargs):
        return self._checkpointer.get_tuple(*args, **kwargs)

    def list(self, *args, **kwargs):
        return self._checkpointer.list(*args, **kwargs)

    def _fenced_write(self, method, *args, **kwargs):
        db = SessionLocal()
        try:
            require_active_investigation_lease(
                db,
                self._execution.investigation_id,
                self._execution.worker_id,
                self._execution.lease_token,
            )
            result = method(*args, **kwargs)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def put(self, *args, **kwargs):
        return self._fenced_write(self._checkpointer.put, *args, **kwargs)

    def put_writes(self, *args, **kwargs):
        return self._fenced_write(self._checkpointer.put_writes, *args, **kwargs)


def psycopg_database_url() -> str:
    url = settings.database_url

    if url.startswith("postgresql+psycopg://"):
        return url.replace(
            "postgresql+psycopg://",
            "postgresql://",
            1,
        )

    return url


@contextmanager
def investigation_graph_runtime():
    connection_string = psycopg_database_url()

    with PostgresSaver.from_conn_string(
        connection_string
    ) as checkpointer:
        checkpointer.setup()

        # Import your EXISTING graph builder here.
        # Replace this import and call with the actual names
        # from your TraceForge project.
        from app.graph.investigation import build_investigation_graph

        execution = current_investigation_execution()
        if execution is None:
            raise RuntimeError(
                "Investigation graph requires an active execution lease."
            )

        graph = build_investigation_graph(
            checkpointer=LeaseFencedCheckpointer(checkpointer, execution)
        )

        yield graph
