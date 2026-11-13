import socket
from uuid import uuid4

import pytest
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from app.graph.runtime import psycopg_database_url


def _postgres_available() -> bool:
    try:
        with socket.create_connection(("localhost", 5432), timeout=1):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="Postgres is not running on localhost:5432",
)


class TestState(TypedDict):
    count: int


def increment(state: TestState) -> TestState:
    return {"count": state["count"] + 1}


def test_postgres_checkpoint_resume():
    thread_id = f"checkpoint-test-{uuid4()}"

    builder = StateGraph(TestState)
    builder.add_node("increment", increment)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)

    with PostgresSaver.from_conn_string(
        psycopg_database_url()
    ) as checkpointer:
        checkpointer.setup()
        graph = builder.compile(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        first = graph.invoke({"count": 1}, config=config)

        assert first["count"] == 2

        # Read the checkpoint saved for this thread.
        snapshot = graph.get_state(config)

        assert snapshot.values["count"] == 2