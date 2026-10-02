# Postgress, sqlalchemy and alembic installation and model creation

```bash
pip install sqlalchemy psycopg[binary] alembic
```
psycopg

This is the PostgreSQL driver.

It actually allows Python to communicate with PostgreSQL.

```bash
SQLAlchemy
    ↓
 psycopg
    ↓
PostgreSQL
```
Alembic

Suppose six months later we add:

```bash
Incident
    ↓
severity
    ↓
severity + priority
```

We don't want to delete our database and recreate everything.

Alembic manages migrations:

```bash 
Database v1
     ↓
Migration
     ↓
Database v2
```

