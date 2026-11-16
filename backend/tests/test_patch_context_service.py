import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Evidence, Incident, Investigation, ProjectConnection, User, Project, AuditEvent, PatchApproval
from app.services.patch_context_service import PatchContextService


class Provider:
    def __init__(self, response="print('ok')\n", error=None):
        self.response, self.error, self.calls = response, error, []

    async def get_file(self, owner, repo, path, ref=None):
        self.calls.append((owner, repo, path, ref))
        if self.error:
            raise self.error
        return self.response


@pytest.fixture
def patch_context_db():
    engine = create_engine("sqlite://")
    tables = [User.__table__, Project.__table__, Incident.__table__, Investigation.__table__, Evidence.__table__, ProjectConnection.__table__, AuditEvent.__table__, PatchApproval.__table__]
    Base.metadata.create_all(engine, tables=tables)
    session = sessionmaker(bind=engine)()
    try:
        user = User(email="patch-user@example.com", password_hash="test")
        other = User(email="patch-other@example.com", password_hash="test")
        session.add_all([user, other]); session.flush()
        project = Project(name="Context project", owner_id=user.id)
        session.add(project); session.commit()
        yield session, user, other, project
    finally:
        session.close(); Base.metadata.drop_all(engine, tables=tables); engine.dispose()


def setup_context(db_session, project_a, user_a, references=("src/app.py",)):
    project_a.description = "unrelated project data"
    incident = Incident(external_id="PC-1", title="Failure", description="Request fails",
                        service="api", severity="HIGH", status="OPEN", project_id=project_a.id)
    db_session.add(incident); db_session.flush()
    investigation = Investigation(incident_id=incident.id, status="COMPLETED", current_stage="DONE")
    db_session.add(investigation); db_session.flush()
    db_session.add(ProjectConnection(project_id=project_a.id, connection_type="code", provider="github",
                                     config={"repository": "trusted-org/service", "branch": "main"}))
    for ref in references:
        db_session.add(Evidence(investigation_id=investigation.id, source_type="code", provider="github",
                                title="Relevant file", content="Failure in handler", source_reference=ref))
    db_session.commit()
    return investigation


def test_authorized_context_uses_owned_connection_and_explicit_references(patch_context_db):
    db_session, user_a, _, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a,
                                  ("https://github.com/trusted-org/service/blob/main/src/app.py",))
    provider = Provider()
    context = asyncio.run(PatchContextService(provider).build_context(db_session, investigation.id, user_a))
    assert context.repository_owner == "trusted-org" and context.repository_name == "service"
    assert provider.calls == [("trusted-org", "service", "src/app.py", "main")]
    assert context.source_files == [{"path": "src/app.py", "content": "print('ok')\n"}]
    assert context.root_cause is None and context.remediation is None
    assert "unrelated project data" not in repr(context.as_dict())


def test_unauthorized_and_missing_investigation_rejected(patch_context_db):
    db_session, user_a, user_b, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a)
    for identifier, user in ((investigation.id, user_b), (99999, user_a)):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(PatchContextService(Provider()).build_context(db_session, identifier, user))
        assert exc.value.status_code == 404


def test_missing_connection_and_evidence_errors(patch_context_db):
    db_session, user_a, _, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a)
    db_session.query(ProjectConnection).delete(); db_session.commit()
    with pytest.raises(HTTPException, match="GitHub code connection"):
        asyncio.run(PatchContextService(Provider()).build_context(db_session, investigation.id, user_a))
    db_session.add(ProjectConnection(project_id=project_a.id, connection_type="code", provider="github",
                                     config={"repository": "trusted-org/service", "branch": "main"}))
    db_session.query(Evidence).filter(Evidence.investigation_id == investigation.id).delete(); db_session.commit()
    with pytest.raises(HTTPException, match="No evidence"):
        asyncio.run(PatchContextService(Provider()).build_context(db_session, investigation.id, user_a))


@pytest.mark.parametrize("reference", ["https://github.com/other/repo/blob/main/a.py", "../secret.py", "/etc/passwd", ".env", "keys/private.pem"])
def test_rejects_foreign_or_invalid_references_before_retrieval(patch_context_db, reference):
    db_session, user_a, _, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a, (reference,))
    provider = Provider()
    with pytest.raises(HTTPException):
        asyncio.run(PatchContextService(provider).build_context(db_session, investigation.id, user_a))
    assert not provider.calls


def test_duplicate_and_count_limits(patch_context_db):
    db_session, user_a, _, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a, ("a.py", "a.py"))
    with pytest.raises(HTTPException, match="Duplicate"):
        asyncio.run(PatchContextService(Provider()).build_context(db_session, investigation.id, user_a))
    db_session.query(Evidence).filter(Evidence.investigation_id == investigation.id).delete()
    for n in range(6):
        db_session.add(Evidence(investigation_id=investigation.id, source_type="code", provider="github",
                                title="file", content="", source_reference=f"{n}.py"))
    db_session.commit()
    with pytest.raises(HTTPException, match="count"):
        asyncio.run(PatchContextService(Provider()).build_context(db_session, investigation.id, user_a))


def test_file_size_invalid_response_and_provider_failure(patch_context_db):
    db_session, user_a, _, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a)
    with pytest.raises(HTTPException, match="100 KB"):
        asyncio.run(PatchContextService(Provider("x" * (100 * 1024 + 1))).build_context(db_session, investigation.id, user_a))
    with pytest.raises(HTTPException, match="ambiguous"):
        asyncio.run(PatchContextService(Provider({"content": [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]})).build_context(db_session, investigation.id, user_a))
    with pytest.raises(HTTPException) as exc:
        asyncio.run(PatchContextService(Provider(error=RuntimeError("sensitive token text"))).build_context(db_session, investigation.id, user_a))
    assert exc.value.status_code == 502 and "sensitive token text" not in str(exc.value.detail)
    with pytest.raises(HTTPException, match="empty"):
        asyncio.run(PatchContextService(Provider(" ")).build_context(db_session, investigation.id, user_a))


def test_no_write_methods_and_missing_source_references(patch_context_db):
    db_session, user_a, _, project_a = patch_context_db
    investigation = setup_context(db_session, project_a, user_a, ("",))
    provider = Provider()
    with pytest.raises(HTTPException):
        asyncio.run(PatchContextService(provider).build_context(db_session, investigation.id, user_a))
    assert not provider.calls
    assert not hasattr(provider, "create_branch") and not hasattr(provider, "create_commit")
