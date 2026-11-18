import os
from uuid import uuid4

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from sqlalchemy.engine import make_url
from typing_extensions import TypedDict

from app.graph.runtime import psycopg_database_url


class CheckpointState(TypedDict):
    count: int


def increment(state: CheckpointState) -> CheckpointState:
    return {"count": state["count"] + 1}


def _build_graph(checkpointer):
    builder = StateGraph(CheckpointState)
    builder.add_node("increment", increment)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)
    return builder.compile(checkpointer=checkpointer)


def test_in_memory_checkpoint_resume_without_external_services():
    thread_id = f"checkpoint-unit-{uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}

    with InMemorySaver() as checkpointer:
        graph = _build_graph(checkpointer)
        result = graph.invoke({"count": 1}, config=config)
        snapshot = graph.get_state(config)

    assert result["count"] == 2
    assert snapshot.values["count"] == 2


def _normalized_database_identity(url: str) -> tuple[str | None, int | None, str | None]:
    parsed = make_url(url)
    return parsed.host, parsed.port, parsed.database


def test_postgres_checkpoint_resume_in_isolated_database():
    checkpoint_url = os.getenv("TRACEFORGE_TEST_CHECKPOINT_DATABASE_URL")
    if not checkpoint_url:
        pytest.skip(
            "Set TRACEFORGE_TEST_CHECKPOINT_DATABASE_URL to a dedicated test database."
        )

    application_url = psycopg_database_url()
    if (
        make_url(checkpoint_url).database == make_url(application_url).database
        or _normalized_database_identity(checkpoint_url)
        == _normalized_database_identity(application_url)
    ):
        pytest.fail(
            "Checkpoint tests refuse to write to the configured application database."
        )

    thread_id = f"checkpoint-test-{uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(checkpoint_url) as checkpointer:
        checkpointer.setup()
        graph = _build_graph(checkpointer)
        try:
            result = graph.invoke({"count": 1}, config=config)
            snapshot = graph.get_state(config)
            assert result["count"] == 2
            assert snapshot.values["count"] == 2
        finally:
            checkpointer.delete_thread(thread_id)
