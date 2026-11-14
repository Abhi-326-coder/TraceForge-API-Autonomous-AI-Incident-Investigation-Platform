import asyncio

import pytest
from fastapi import HTTPException

from app.db.models import Incident, Investigation, PatchApproval, Project, ProjectConnection
from app.routes import incidents as incident_routes
from app.routes.connections import create_connection, list_connections
from app.schemas.approval import ApprovalDecision
from app.schemas.connection import ConnectionCreate
from app.services.approval_service import decide_patch_approval, get_patch_approval
from app.services.github_branch_service import create_branch_for_approval
from app.services.github_pr_service import commit_approved_patch
from app.services import github_branch_service, github_pr_service


def owned_resources(db_session, user_b):
    project = Project(name="B private project", owner_id=user_b.id)
    db_session.add(project)
    db_session.flush()
    incident = Incident(external_id="B-001", title="Private", description="Private", service="private", severity="HIGH", status="OPEN", project_id=project.id)
    db_session.add(incident)
    db_session.flush()
    investigation = Investigation(incident_id=incident.id, status="COMPLETED", current_stage="DONE")
    db_session.add(investigation)
    db_session.flush()
    patch = PatchApproval(investigation_id=investigation.id, patch_summary="Private fix", diff="diff", changed_files=["a.py"], proposed_files={"a.py": "new"}, tests_to_run=["pytest"], risks=["risk"], status="PENDING", patch_sha256="hash")
    connection = ProjectConnection(project_id=project.id, connection_type="github", provider="github", config={"repo": "private"})
    db_session.add_all([patch, connection])
    db_session.commit()
    return project, incident, patch


def test_incident_routes_scope_list_and_direct_access(db_session, user_a, user_b, monkeypatch):
    project_b, incident_b, _ = owned_resources(db_session, user_b)
    project_a = Project(name="A project", owner_id=user_a.id)
    db_session.add(project_a); db_session.flush()
    incident_a = Incident(external_id="A-001", title="Owned", description="Owned", service="owned", severity="LOW", status="OPEN", project_id=project_a.id)
    db_session.add(incident_a); db_session.commit()
    assert [incident.id for incident in incident_routes.list_incidents(db_session, user_a)] == [incident_a.id]
    with pytest.raises(HTTPException) as exc: incident_routes.get_incident_by_id(incident_b.id, db_session, user_a)
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc: incident_routes.get_incident_logs(incident_b.id, db_session, user_a)
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc: incident_routes.get_incident_metrics(incident_b.id, db_session, user_a)
    assert exc.value.status_code == 404
    monkeypatch.setattr(incident_routes, "get_logs", lambda _: [])
    monkeypatch.setattr(incident_routes, "get_metrics", lambda _: {"request_rate": 1, "error_rate": 0, "latency_ms": 1, "database_connections": 1, "database_connection_limit": 2})
    assert incident_routes.get_incident_by_id(incident_a.id, db_session, user_a).id == incident_a.id


def test_patch_decision_and_github_services_require_patch_owner(db_session, user_a, user_b, monkeypatch):
    _, _, patch = owned_resources(db_session, user_b)
    class UnexpectedGitHubWrite:
        def __init__(self): raise AssertionError("GitHub provider must not be constructed before authorization")
    monkeypatch.setattr(github_branch_service, "GitHubRESTProvider", UnexpectedGitHubWrite)
    monkeypatch.setattr(github_pr_service, "GitHubWriteProvider", UnexpectedGitHubWrite)
    with pytest.raises(HTTPException) as exc: get_patch_approval(db_session, patch.id, current_user=user_a)
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc: decide_patch_approval(db_session, patch.id, ApprovalDecision(decision="APPROVED"), current_user=user_a)
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc: asyncio.run(create_branch_for_approval(db_session, user_a, patch.id, "owner", "repo", "main"))
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc: asyncio.run(commit_approved_patch(db_session, user_a, patch.id, "owner", "repo", "main"))
    assert exc.value.status_code == 404
    approved = decide_patch_approval(db_session, patch.id, ApprovalDecision(decision="APPROVED", note="Reviewed"), current_user=user_b)
    assert approved.status == "APPROVED" and approved.decided_by == str(user_b.id) and approved.decided_at is not None
    with pytest.raises(HTTPException) as exc: decide_patch_approval(db_session, patch.id, ApprovalDecision(decision="REJECTED"), current_user=user_b)
    assert exc.value.status_code == 409


def test_connections_require_project_owner(db_session, user_a, user_b):
    project_b, _, _ = owned_resources(db_session, user_b)
    with pytest.raises(HTTPException) as exc: list_connections(project_b.id, db_session, user_a)
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc: create_connection(project_b.id, ConnectionCreate(connection_type="github", provider="github", config={}), db_session, user_a)
    assert exc.value.status_code == 404
    assert len(list_connections(project_b.id, db_session, user_b)) == 1
