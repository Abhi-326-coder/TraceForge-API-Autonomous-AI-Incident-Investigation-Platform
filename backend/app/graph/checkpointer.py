from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings


def get_checkpointer():
    """
    Create a PostgreSQL-backed LangGraph checkpointer.

    The returned object owns a database connection pool.
    Keep it alive for the lifetime of the worker process.
    """
    checkpointer = PostgresSaver.from_conn_string(
        settings.database_url.replace(
            "postgresql+psycopg://",
            "postgresql://",
            1,
        )
    )

    return checkpointer