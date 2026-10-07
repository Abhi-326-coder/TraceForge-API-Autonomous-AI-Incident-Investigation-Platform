from app.db.database import SessionLocal
from app.rag.knowledge_service import KnowledgeService


RUNBOOK = """
Checkout API Database Connection Pool Runbook

The checkout-api service uses a PostgreSQL connection pool.

Symptoms of connection pool exhaustion include:

- HTTP 500 errors from checkout requests
- increased request latency
- database timeout errors
- messages indicating that the connection pool is exhausted
- database connection utilization approaching the configured limit

When investigating connection pool exhaustion:

1. Check database connection utilization.
2. Check application logs for connection pool errors.
3. Check whether recent deployments changed database configuration.
4. Check for connections that are not being returned to the pool.
5. Verify pool size and timeout configuration.

If active database connections approach the configured maximum,
new checkout requests may fail.

Do not immediately increase the pool size without checking
the database's maximum connection capacity.
"""


def main():

    db = SessionLocal()

    service = KnowledgeService()

    service.ingest_document(
        db=db,
        project_id=1,
        title="Checkout Database Connection Pool Runbook",
        content=RUNBOOK,
        source="internal-runbook://checkout/database-pool",
    )

    db.close()

    print("Knowledge seeded.")


if __name__ == "__main__":
    main()