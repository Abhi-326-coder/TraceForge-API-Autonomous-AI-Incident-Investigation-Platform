# Alembic Initialize Alembic

From:

traceforge/backend

run:

```bash
alembic init alembic
```

You'll get:

```bash
backend/
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── alembic.ini
└── app/```
8.9 Tell Alembic about our models

Open:

backend/alembic/env.py

Find:

target_metadata = None

Replace it with:

from app.db.database import Base
from app.db import models

target_metadata = Base.metadata

The import:

from app.db import models

is important.

It ensures SQLAlchemy knows about:

Project
Incident

when Alembic examines the metadata.

8.10 Configure the database URL

Open:

backend/alembic.ini

Find:

sqlalchemy.url = driver://user:pass@localhost/dbname

Change it to:

sqlalchemy.url = postgresql+psycopg://traceforge:traceforge@localhost:5432/traceforge

For our local development setup, that's fine.

Later we'll move this into environment variables.

8.11 Generate our first migration

Run:

alembic revision --autogenerate -m "create projects and incidents"

Alembic should detect:

projects
incidents

A migration file will appear inside:

alembic/versions/

Something like:

alembic/
└── versions/
    └── abc123_create_projects_and_incidents.py

Don't manually edit it yet.

8.12 Apply the migration

Run:

alembic upgrade head

Now PostgreSQL should contain:

traceforge
│
├── projects
├── incidents
└── alembic_version

You can verify using:

docker exec -it traceforge-postgres psql -U traceforge -d traceforge

Inside PostgreSQL:

\dt

You should see:

alembic_version
incidents
projects

Exit:

\q