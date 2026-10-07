from sqlalchemy.orm import Session

from app.db.models import KnowledgeDocument
from app.rag.chunking import chunk_text
from app.rag.embeddings import GeminiEmbeddingService


class KnowledgeService:

    def __init__(self):

        self.embedding_service = (
            GeminiEmbeddingService()
        )

    def ingest_document(
        self,
        db: Session,
        project_id: int,
        title: str,
        content: str,
        source: str,
    ):

        chunks = chunk_text(
            content
        )

        documents = []

        for index, chunk in enumerate(chunks):

            embedding = (
                self.embedding_service.embed(
                    chunk
                )
            )

            document = KnowledgeDocument(
                project_id=project_id,
                title=title,
                content=chunk,
                source=source,
                chunk_index=index,
                embedding=embedding,
            )

            db.add(document)

            documents.append(document)

        db.commit()

        return documents
    
    def search(
        self,
        db: Session,
        project_id: int,
        query: str,
        top_k: int = 5,
    ):
        query_embedding = (
            self.embedding_service.embed(
                query
            )
        )

        distance = (
            KnowledgeDocument.embedding.cosine_distance(
                query_embedding
            )
        )

        results = (
            db.query(
                KnowledgeDocument,
                distance.label("distance"),
            )
            .filter(
                KnowledgeDocument.project_id
                == project_id
            )
            .order_by(distance)
            .limit(top_k)
            .all()
        )

        return results