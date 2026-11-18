import re

from sqlalchemy.orm import Session

from app.db.models import User, Investigation, Incident
from app.providers.github_rest import GitHubRESTProvider
from app.services.authorization_service import get_patch_github_repository, get_owned_patch
from app.services.audit_service import record_audit_event
from app.config import settings


async def create_branch_for_approval(
    db: Session,
    current_user: User,
    patch_id: int,
    owner: str,
    repo: str,
    base_branch: str,
) -> dict:
    # Request target values are retained for API compatibility but never trusted.
    if settings.demo_mode:
        approval = get_owned_patch(db, patch_id, current_user)
        investigation = db.get(Investigation, approval.investigation_id)
        project_id = db.get(Incident, investigation.incident_id).project_id
    else:
        approval, project_id, owner, repo, base_branch = get_patch_github_repository(db, patch_id, current_user)

    if approval.status != "APPROVED":
        raise ValueError(
            "Patch must be approved before branch creation"
        )

    if not approval.diff.strip():
        raise ValueError("Approved patch has no diff")

    # Stable branch name for retries.
    branch_name = (
        f"traceforge/incident-{approval.investigation_id}"
        f"-patch-{approval.id}"
    )

    if not re.fullmatch(
        r"traceforge/incident-[0-9]+-patch-[0-9]+",
        branch_name,
    ):
        raise ValueError("Invalid generated branch name")

    if approval.github_branch:
        result = {
            "branch_name": approval.github_branch,
            "sha": approval.github_branch_sha or "",
            "url": approval.github_branch_url or "",
        }
        if approval.github_branch_sha == "SIMULATED":
            result.update(simulated=True, message="Demo only: branch creation was simulated; no GitHub branch was written.")
        return result

    if settings.demo_mode:
        approval.github_branch = f"traceforge/incident-{approval.investigation_id}-patch-{approval.id}"
        approval.github_branch_sha = "SIMULATED"
        approval.github_branch_url = None
        db.commit()
        return {"branch_name": approval.github_branch, "sha": "SIMULATED", "url": "", "simulated": True, "message": "Demo only: branch creation was simulated; no GitHub branch was written."}

    provider = GitHubRESTProvider()
    try:
        result = await provider.create_branch(owner=owner, repo=repo, base_branch=base_branch, new_branch=branch_name)
        approval.github_branch = result["branch_name"]
        approval.github_branch_sha = result["sha"]
        approval.github_branch_url = result["url"]
        record_audit_event(db, action="GITHUB_BRANCH_CREATED", outcome="SUCCESS", actor_user_id=current_user.id, resource_type="PatchApproval", resource_id=approval.id, metadata={"patch_id": approval.id, "project_id": project_id, "repository": f"{owner}/{repo}", "branch": approval.github_branch})
        db.commit()
        return result
    except Exception:
        db.rollback()
        record_audit_event(db, action="GITHUB_BRANCH_CREATED", outcome="FAILURE", actor_user_id=current_user.id, resource_type="PatchApproval", resource_id=approval.id, metadata={"patch_id": approval.id, "project_id": project_id, "repository": f"{owner}/{repo}", "reason_code": "github_write_failed"})
        db.commit()
        raise
