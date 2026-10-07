## Add the RAG Knowledge Server connecting with pgvector and Knowledge mcp server

- First we are going to change the image in docker compose from postgres to ``pgvector/pgvector:pg16``

- Install the pgvector packege in backend and update the requirements.txt

- Run the alembic revision : ``alembic revision -m "add knowledge documents"``

Open the generated migration and use:

```python
from alembic import op
import sqlalchemy as sa

from pgvector.sqlalchemy import Vector


def upgrade():

    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )

    op.create_table(
        "knowledge_documents",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id"),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "embedding",
            Vector(768),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade():

    op.drop_table(
        "knowledge_documents"
    )
```
- Creating a Vector database in using pgvector having below columns
```bash
id
project_id
title
content
source
chunk_index
embedding
created_at
```

- Run ``alembic upgrade head``

- In the model.py add below model

```python
class KnowledgeDocument(Base):

    __tablename__ = "knowledge_documents"

    id = Column(
        Integer,
        primary_key=True,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    source = Column(
        String,
        nullable=False,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    embedding = Column(
        Vector(768),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
```
- Add the embidding using google genai model in ``embeddings.py``

- ``chunking.py``

- ``knowledge_service.py``

- Add the seeded data in``` scripts/seed_knowledge.py``` and it is tested and working well

- Added the ``test_rag.py`` to test Knowledge and is working properly

- Add the ``knowledge_server.py`` 

 ```bash
                           INCIDENT
                              │
                              ▼
                         SUPERVISOR
                              │
         ┌────────────────────┼───────────────────┐
         ▼                    ▼                   ▼
      LOG AGENT          METRICS AGENT        CODE AGENT
         │                    │                   │
      Logs MCP             Metrics MCP        GitHub MCP
         │                    │                   │
         ▼                    ▼                   ▼
      Logs                 Metrics             Source
                                                   │
         └────────────────────┬────────────────────┘
                              ▼
                         KNOWLEDGE MCP
                              │
                              ▼
                           pgvector
                              │
                       ┌──────┼──────┐
                       ▼      ▼      ▼
                    Runbooks Docs Postmortems
                              │
                              ▼
                          EVIDENCE
                              │
                              ▼
                      ROOT CAUSE AGENT
```