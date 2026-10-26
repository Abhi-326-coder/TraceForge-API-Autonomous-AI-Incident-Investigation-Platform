import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Project, User


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://")
    tables = [User.__table__, Project.__table__]
    Base.metadata.create_all(engine, tables=tables)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine, tables=tables)
        engine.dispose()


@pytest.fixture
def user_a(db_session):
    user = User(email="user-a@example.com", password_hash="test-hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_b(db_session):
    user = User(email="user-b@example.com", password_hash="test-hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def project_a(db_session, user_a):
    project = Project(name="Project A", owner_id=user_a.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project
