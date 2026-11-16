import pytest
from fastapi import HTTPException

from app.db.models import Incident, Investigation, PatchApproval, Project, AuditEvent
from app.services import generated_patch_persistence_service as persistence
from app.services.approval_service import calculate_patch_hash


def setup_investigation(db_session, user, external_id="GEN-1"):
    project = Project(name="Generated patch", owner_id=user.id)
    db_session.add(project); db_session.flush()
    incident = Incident(external_id=external_id, title="Failure", description="Broken API",
                        service="api", severity="HIGH", status="OPEN", project_id=project.id)
    db_session.add(incident); db_session.flush()
    investigation = Investigation(incident_id=incident.id, status="COMPLETED", current_stage="DONE")
    db_session.add(investigation); db_session.commit()
    return investigation


def generated():
    class Result:
        summary = "Handle API error"
        diff = "--- a/src/api.py\n+++ b/src/api.py\n"
        changed_files = ["src/api.py"]
        tests_to_run = ["pytest tests/api"]
        risks = ["Changes error handling"]
        proposed_files = {"src/api.py": "raise ValueError()\n"}
    return Result()


def test_success_persists_pending_patch_with_mapped_fields(db_session, user_a):
    investigation = setup_investigation(db_session, user_a)
    patch = persistence.persist_generated_patch(db_session, investigation.id, generated(), current_user=user_a)
    assert patch.investigation_id == investigation.id
    assert patch.status == "PENDING"
    assert patch.patch_summary == "Handle API error"
    assert patch.diff.startswith("--- a/src/api.py")
    assert patch.changed_files == ["src/api.py"]
    assert patch.tests_to_run == ["pytest tests/api"]
    assert patch.risks == ["Changes error handling"]
    assert patch.proposed_files == {"src/api.py": "raise ValueError()\n"}
    assert patch.patch_sha256 == calculate_patch_hash(patch.diff, patch.proposed_files, patch.changed_files)


def test_missing_or_inconsistent_proposed_contents_rejected(db_session, user_a):
    investigation = setup_investigation(db_session, user_a)
    result = generated()
    result.proposed_files = {}
    with pytest.raises(HTTPException):
        persistence.persist_generated_patch(db_session, investigation.id, result, current_user=user_a)
    result.proposed_files = {"other.py": "contents"}
    with pytest.raises(HTTPException):
        persistence.persist_generated_patch(db_session, investigation.id, result, current_user=user_a)
    assert db_session.query(PatchApproval).count() == 0


def test_unauthorized_user_rejected_before_persistence(db_session, user_a, user_b):
    investigation = setup_investigation(db_session, user_a)
    with pytest.raises(HTTPException) as exc:
        persistence.persist_generated_patch(db_session, investigation.id, generated(), current_user=user_b)
    assert exc.value.status_code == 404
    assert db_session.query(PatchApproval).count() == 0


def test_persistence_failure_rolls_back(db_session, user_a, monkeypatch):
    investigation = setup_investigation(db_session, user_a)
    def fail_commit():
        raise RuntimeError("database failure")
    monkeypatch.setattr(db_session, "commit", fail_commit)
    with pytest.raises(RuntimeError):
        persistence.persist_generated_patch(db_session, investigation.id, generated(), current_user=user_a)
    assert db_session.query(PatchApproval).count() == 0
    assert db_session.query(AuditEvent).filter(AuditEvent.action == "PATCH_CREATED").count() == 0


def test_repeated_calls_create_separate_pending_proposals(db_session, user_a):
    investigation = setup_investigation(db_session, user_a)
    first = persistence.persist_generated_patch(db_session, investigation.id, generated(), current_user=user_a)
    second = persistence.persist_generated_patch(db_session, investigation.id, generated(), current_user=user_a)
    assert first.id != second.id
    assert db_session.query(PatchApproval).filter(PatchApproval.investigation_id == investigation.id).count() == 2


def test_no_github_write_service_is_used(db_session, user_a, monkeypatch):
    investigation = setup_investigation(db_session, user_a)
    def unexpected(*args, **kwargs):
        raise AssertionError("GitHub write operation must not be called")
    monkeypatch.setattr("app.services.github_branch_service.create_branch_for_approval", unexpected)
    monkeypatch.setattr("app.services.github_pr_service.commit_approved_patch", unexpected)
    patch = persistence.persist_generated_patch(db_session, investigation.id, generated(), current_user=user_a)
    assert patch.status == "PENDING" and patch.github_branch is None and patch.github_pr_number is None
