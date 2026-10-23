from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings


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
        # Import your EXISTING graph builder here.
        # Replace this import and call with the actual names
        # from your TraceForge project.
        from app.graph.investigation import build_investigation_graph

        graph = build_investigation_graph(
            checkpointer=checkpointer
        )

        yield graph