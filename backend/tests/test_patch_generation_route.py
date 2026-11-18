import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.db.models import AuditEvent, Incident, Investigation, PatchApproval, Project, ProjectConnection, User
from app.routes import approvals
from app.schemas.patch import GeneratedPatch
from app.security import get_current_user


@pytest.fixture
def route_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    tables = [User.__table__, Project.__table__, Incident.__table__, Investigation.__table__,
              PatchApproval.__table__, ProjectConnection.__table__, AuditEvent.__table__]
    Base.metadata.create_all(engine, tables=tables)
    db_session = sessionmaker(bind=engine)()
    user_a = User(email="route-user@example.com", password_hash="test")
    db_session.add(user_a); db_session.flush()
    project_a = Project(name="Route project", owner_id=user_a.id)
    db_session.add(project_a); db_session.commit()
    app = FastAPI()
    app.include_router(approvals.router)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: user_a
    try:
        with TestClient(app) as client:
            client.db_session = db_session
            client.user = user_a
            client.project = project_a
            yield client
    finally:
        app.dependency_overrides.clear()
        db_session.close(); Base.metadata.drop_all(engine, tables=tables); engine.dispose()


def test_generation_route_persists_response_pending_and_never_writes_github(route_client, monkeypatch):
    db_session, user_a, project_a = route_client.db_session, route_client.user, route_client.project
    incident = Incident(external_id="ROUTE-1", title="Failure", description="", service="api",
                        severity="HIGH", status="OPEN", project_id=project_a.id)
    db_session.add(incident); db_session.flush()
    investigation = Investigation(incident_id=incident.id, status="COMPLETED", current_stage="DONE")
    db_session.add(investigation); db_session.commit()
    generated = GeneratedPatch(summary="Proposal", diff="diff", changed_files=["app.py"],
                              proposed_files={"app.py": "complete contents"})
    calls = []

    class Generation:
        async def generate(self, db, investigation_id, user):
            calls.append(("generate", investigation_id, user.id))
            return generated

    class Persistence:
        def persist(self, db, investigation_id, result, user):
            from app.services.generated_patch_persistence_service import persist_generated_patch
            calls.append(("persist", investigation_id, result is generated, user.id))
            return persist_generated_patch(db, investigation_id, result, current_user=user)

    monkeypatch.setattr(approvals, "PatchGenerationService", Generation)
    monkeypatch.setattr(approvals, "GeneratedPatchPersistenceService", Persistence)
    response = route_client.post("/api/patches/generate", json={"investigation_id": investigation.id})
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["investigation_id"] == investigation.id
    assert payload["patch_summary"] == "Proposal" and payload["status"] == "PENDING"
    assert payload["proposed_files"] == {"app.py": "complete contents"}
    assert set(payload) >= {"id", "diff", "changed_files", "tests_to_run", "risks", "created_at"}
    assert [call[0] for call in calls] == ["generate", "persist"]
    assert not hasattr(Generation, "create_branch") and not hasattr(Persistence, "commit_approved_patch")


def test_route_rejects_invalid_and_extra_client_fields(route_client):
    assert route_client.post("/api/patches/generate", json={"investigation_id": 0}).status_code == 422
    assert route_client.post("/api/patches/generate", json={"investigation_id": 1, "diff": "client"}).status_code == 422


def test_unauthenticated_request_rejected(db_session, monkeypatch):
    app = FastAPI(); app.include_router(approvals.router)
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        response = client.post("/api/patches/generate", json={"investigation_id": 1})
    assert response.status_code == 401


@pytest.mark.parametrize("status,detail", [
    (404, "Investigation not found."),
    (409, "Project has no GitHub code connection."),
    (422, "Evidence source-file references are missing."),
    (502, "Patch generation failed."),
])
def test_context_and_ai_errors_propagate(status, detail, route_client, monkeypatch):
    class Generation:
        async def generate(self, *args):
            from fastapi import HTTPException
            raise HTTPException(status, detail)
    class Persistence:
        def persist(self, *args):
            raise AssertionError("Must not persist after failed generation")
    monkeypatch.setattr(approvals, "PatchGenerationService", Generation)
    monkeypatch.setattr(approvals, "GeneratedPatchPersistenceService", Persistence)
    response = route_client.post("/api/patches/generate", json={"investigation_id": 18})
    assert response.status_code == status and detail in response.text


def test_persistence_failure_rolls_back_and_returns_safe_error(route_client, monkeypatch):
    class Generation:
        async def generate(self, *args):
            return GeneratedPatch(summary="safe", diff="diff", changed_files=["x.py"],
                                  proposed_files={"x.py": "contents"})
    class Persistence:
        def persist(self, *args):
            raise RuntimeError("sensitive persistence internals")
    monkeypatch.setattr(approvals, "PatchGenerationService", Generation)
    monkeypatch.setattr(approvals, "GeneratedPatchPersistenceService", Persistence)
    response = route_client.post("/api/patches/generate", json={"investigation_id": 18})
    assert response.status_code == 500
    assert "sensitive persistence internals" not in response.text
