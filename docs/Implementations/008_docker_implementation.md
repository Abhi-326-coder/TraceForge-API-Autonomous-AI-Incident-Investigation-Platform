# Implementation of Docker of Postgres image

```yaml
services:

  postgres:
    image: postgres:16
    container_name: traceforge-postgres

    environment:
      POSTGRES_USER: traceforge
      POSTGRES_PASSWORD: traceforge
      POSTGRES_DB: traceforge

    ports:
      - "5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

DATABASE_URL = (
    "postgresql+psycopg://"
    "traceforge:traceforge@localhost:5432/traceforge"
)


```bash 
postgresql+psycopg://
traceforge:traceforge
@
localhost:5432
/
traceforge
```

which means:

```bash
database type  → PostgreSQL
driver         → psycopg
username       → traceforge
password       → traceforge
host           → localhost
port           → 5432
database       → traceforge```