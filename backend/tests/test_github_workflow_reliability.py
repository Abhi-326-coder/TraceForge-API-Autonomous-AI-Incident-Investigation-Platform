import asyncio

import pytest

from app.db.models import AuditEvent, Incident, Investigation, PatchApproval, Project, ProjectConnection
from app.services.approval_service import calculate_patch_hash
from app.services import github_branch_service, github_pr_service


def workflow_patch(db, user):
    project = Project(name="Workflow", owner_id=user.id)
    db.add(project); db.flush()
    db.add(ProjectConnection(project_id=project.id, connection_type="code", provider="github", config={"repository": "trusted-org/trusted-repo", "branch": "main"}))
    incident = Incident(external_id="WF-1", title="Workflow", description="", service="svc", severity="HIGH", status="OPEN", project_id=project.id)
    db.add(incident); db.flush()
    investigation = Investigation(incident_id=incident.id, status="COMPLETED", current_stage="DONE")
    db.add(investigation); db.flush()
    patch = PatchApproval(investigation_id=investigation.id, patch_summary="Fix", diff="diff", changed_files=["app.py"], proposed_files={"app.py": "new"}, tests_to_run=["pytest"], risks=["risk"], status="APPROVED")
    patch.patch_sha256 = calculate_patch_hash(patch.diff, patch.proposed_files, patch.changed_files)
    db.add(patch); db.commit(); return project, patch


def test_branch_uses_connection_persists_and_is_idempotent(db_session, user_a, monkeypatch):
    project, patch = workflow_patch(db_session, user_a)
    calls = []
    class Provider:
        async def create_branch(self, **kwargs):
            calls.append(kwargs); return {"branch_name": "traceforge/incident-1-patch-1", "sha": "a" * 40, "url": "https://api.github.test/ref"}
    monkeypatch.setattr(github_branch_service, "GitHubRESTProvider", Provider)
    first = asyncio.run(github_branch_service.create_branch_for_approval(db_session, user_a, patch.id, "evil", "repo", "other"))
    second = asyncio.run(github_branch_service.create_branch_for_approval(db_session, user_a, patch.id, "evil", "repo", "other"))
    db_session.refresh(patch)
    assert first == second and len(calls) == 1
    assert calls[0]["owner"] == "trusted-org" and calls[0]["repo"] == "trusted-repo" and calls[0]["base_branch"] == "main"
    assert patch.github_branch and patch.github_branch_sha == "a" * 40
    event = db_session.query(AuditEvent).filter(AuditEvent.action == "GITHUB_BRANCH_CREATED").one()
    assert event.outcome == "SUCCESS" and event.event_metadata["project_id"] == project.id


def test_pr_uses_persisted_branch_and_does_not_duplicate(db_session, user_a, monkeypatch):
    _, patch = workflow_patch(db_session, user_a)
    patch.github_branch = "traceforge/incident-1-patch-1"; db_session.commit()
    calls = []
    class Provider:
        async def create_commit_and_pr(self, **kwargs):
            calls.append(kwargs); return {"commit_sha": "b" * 40, "branch": kwargs["head_branch"], "pr_number": 42, "pr_url": "https://github.test/pr/42", "pr_state": "open", "draft": True}
    monkeypatch.setattr(github_pr_service, "GitHubWriteProvider", Provider)
    first = asyncio.run(github_pr_service.commit_approved_patch(db_session, user_a, patch.id, "evil", "repo", "other"))
    second = asyncio.run(github_pr_service.commit_approved_patch(db_session, user_a, patch.id, "evil", "repo", "other"))
    assert first == second and len(calls) == 1
    assert calls[0]["owner"] == "trusted-org" and calls[0]["head_branch"] == patch.github_branch
    assert db_session.query(AuditEvent).filter(AuditEvent.action == "GITHUB_PR_CREATED", AuditEvent.outcome == "SUCCESS").count() == 1


def test_github_failure_does_not_persist_success_state_and_is_audited(db_session, user_a, monkeypatch):
    _, patch = workflow_patch(db_session, user_a)
    class Provider:
        async def create_branch(self, **kwargs): raise RuntimeError("provider failed")
    monkeypatch.setattr(github_branch_service, "GitHubRESTProvider", Provider)
    with pytest.raises(RuntimeError): asyncio.run(github_branch_service.create_branch_for_approval(db_session, user_a, patch.id, "x", "y", "z"))
    db_session.refresh(patch)
    assert patch.github_branch is None
    assert db_session.query(AuditEvent).filter(AuditEvent.action == "GITHUB_BRANCH_CREATED", AuditEvent.outcome == "FAILURE").count() == 1
