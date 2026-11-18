from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db.models import AuditEvent, Evidence, Incident, Investigation, PatchApproval, Project, ProjectConnection, User
from app.routes.approvals import router
from app.schemas.patch import GeneratedPatch
from app.security import get_current_user
from app.services.approval_service import decide_patch_approval
from app.schemas.approval import ApprovalDecision


def test_generation_persistence_detail_and_approval_pipeline(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    tables = [User.__table__, Project.__table__, Incident.__table__, Investigation.__table__,
              Evidence.__table__, ProjectConnection.__table__, PatchApproval.__table__, AuditEvent.__table__]
    Base.metadata.create_all(engine, tables=tables)
    db = sessionmaker(bind=engine)()
    owner = User(email="pipe-owner@example.com", password_hash="test")
    stranger = User(email="pipe-stranger@example.com", password_hash="test")
    db.add_all([owner, stranger]); db.flush()
    project = Project(name="Pipeline", owner_id=owner.id); db.add(project); db.flush()
    incident = Incident(external_id="PIPE-1", title="Incident", description="fails", service="api", severity="HIGH", status="OPEN", project_id=project.id)
    db.add(incident); db.flush()
    investigation = Investigation(incident_id=incident.id, status="COMPLETED", current_stage="DONE")
    db.add(investigation); db.flush()
    db.add(ProjectConnection(project_id=project.id, connection_type="code", provider="github", config={"repository": "org/repo", "branch": "main"}))
    db.add(Evidence(investigation_id=investigation.id, source_type="code", provider="github", title="Source", content="affected file", source_reference="src/app.py"))
    db.commit()

    reads = []
    class ReadProvider:
        async def get_file(self, owner, repo, path, ref=None):
            reads.append((owner, repo, path, ref))
            return "original code\n"
    class MockAgent:
        def __init__(self): pass
        def generate(self, **kwargs):
            assert kwargs["source_files"] == [{"path": "src/app.py", "content": "original code\n"}]
            return GeneratedPatch(summary="Fix", diff="diff", changed_files=["src/app.py"],
                                  proposed_files={"src/app.py": "complete fixed file\n"})
    monkeypatch.setattr("app.services.patch_context_service.GitHubMCPProvider", ReadProvider)
    monkeypatch.setattr("app.services.patch_generation_service.PatchAgent", MockAgent)

    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: owner
    try:
        with TestClient(app) as client:
            generated = client.post("/api/patches/generate", json={"investigation_id": investigation.id})
            assert generated.status_code == 201, generated.text
            patch_id = generated.json()["id"]
            assert generated.json()["status"] == "PENDING"
            assert generated.json()["proposed_files"] == {"src/app.py": "complete fixed file\n"}
            detail = client.get(f"/api/patches/{patch_id}")
            assert detail.status_code == 200
            assert detail.json()["proposed_files"] == generated.json()["proposed_files"]
            app.dependency_overrides[get_current_user] = lambda: stranger
            assert client.get(f"/api/patches/{patch_id}").status_code == 404
            app.dependency_overrides[get_current_user] = lambda: owner
        assert reads == [("org", "repo", "src/app.py", "main")]
        approved = decide_patch_approval(db, patch_id, ApprovalDecision(decision="APPROVED", note="Reviewed"), current_user=owner)
        assert approved.status == "APPROVED"
        try:
            decide_patch_approval(db, patch_id, ApprovalDecision(decision="REJECTED"), current_user=owner)
        except HTTPException as exc:
            assert exc.status_code == 409
        else:
            raise AssertionError("A second decision should be rejected")
        # Approved workflow is covered by the existing mocked GitHub reliability test.
    finally:
        app.dependency_overrides.clear(); db.close(); Base.metadata.drop_all(engine, tables=tables); engine.dispose()
