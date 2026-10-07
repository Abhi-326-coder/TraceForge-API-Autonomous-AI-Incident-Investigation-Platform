from app.db.database import SessionLocal
from app.rag.knowledge_service import KnowledgeService


db = SessionLocal()

service = KnowledgeService()

results = service.search(
    db=db,
    project_id=1,
    query=(
        "Why is checkout-api returning HTTP 500 "
        "errors because of database connections?"
    ),
    top_k=3,
)

for document, distance in results:

    print("\nTITLE:")
    print(document.title)

    print("\nSOURCE:")
    print(document.source)

    print("\nCONTENT:")
    print(document.content)

    print("\nDISTANCE:")
    print(distance)


db.close()