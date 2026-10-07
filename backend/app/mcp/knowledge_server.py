from mcp.server import MCPServer

from app.db.database import SessionLocal
from app.rag.knowledge_service import KnowledgeService

mcp = MCPServer(
    "traceforge-knowledge"
)

@mcp.tool()
def search_knowledge(
    project_id: int,
    query: str,
) -> dict:
    """
    Search internal TraceForge knowledge such as
    runbooks, architecture documentation,
    incident postmortems and troubleshooting guides.
    """

    db = SessionLocal()

    try:

        service = KnowledgeService()

        results = service.search(
            db=db,
            project_id=project_id,
            query=query,
            top_k=5,
        )

        return {
            "results": [
                {
                    "title": document.title,
                    "content": document.content,
                    "source": document.source,
                    "chunk_index": document.chunk_index,
                    "similarity_distance": float(
                        distance
                    ),
                }
                for document, distance in results
            ]
        }

    finally:
        db.close()

if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8102,
    )