from app.db.database import SessionLocal
from app.services.evidence_service import create_evidence


db = SessionLocal()


create_evidence(
    db=db,
    investigation_id=1,
    source_type="logs",
    provider="simulator",
    title="Database connection pool exhausted",
    content="Database connection pool exhausted",
    source_reference="simulator://logs/checkout-api/001",
)


create_evidence(
    db=db,
    investigation_id=1,
    source_type="metrics",
    provider="simulator",
    title="Database connection utilization",
    content="98 database connections active out of a maximum of 100.",
    source_reference="simulator://metrics/checkout-api/database_connections",
)


create_evidence(
    db=db,
    investigation_id=1,
    source_type="logs",
    provider="simulator",
    title="Checkout transaction failed",
    content="Failed to execute checkout transaction.",
    source_reference="simulator://logs/checkout-api/002",
)


db.close()

print("Evidence seeded successfully.")