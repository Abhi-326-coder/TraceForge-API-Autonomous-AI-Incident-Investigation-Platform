import hashlib
import json

from sqlalchemy.orm import Session

from app.db.models import PatchApproval, User
from app.providers.github_writes import GitHubWriteProvider
from app.services.authorization_service import get_patch_github_repository
from app.services.audit_service import record_audit_event


def calculate_patch_hash(approval: PatchApproval) -> str:
    # Bind the hash to BOTH the diff and the proposed file contents.
    payload = json.dumps(
        {
            "diff": approval.diff,
            "proposed_files": approval.proposed_files,
            "changed_files": approval.changed_files,
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def commit_approved_patch(
    db: Session,
    current_user: User,
    patch_id: int,
    owner: str,
    repo: str,
    base_branch: str,
) -> dict:
    # Request target values are retained for API compatibility but never trusted.
    approval, project_id, owner, repo, base_branch = get_patch_github_repository(db, patch_id, current_user)

    if approval.status != "APPROVED":
        raise ValueError("Patch must be approved first")

    if not approval.proposed_files:
        raise ValueError(
            "Approved file contents are missing; regenerate the patch"
        )

    if not approval.patch_sha256:
        raise ValueError(
            "Patch integrity hash is missing; re-create the approval"
        )

    actual_hash = calculate_patch_hash(approval)

    if actual_hash != approval.patch_sha256:
        raise ValueError(
            "Patch integrity verification failed"
        )

    expected_paths = set(approval.changed_files)
    actual_paths = set(approval.proposed_files.keys())

    if expected_paths != actual_paths:
        raise ValueError(
            "Proposed file paths do not match the approved file list"
        )

    branch = approval.github_branch

    if not branch:
        raise ValueError(
            "Create the feature branch before committing the patch"
        )

    if approval.github_pr_number:
        return {"commit_sha": approval.github_commit_sha, "branch": branch, "pr_number": approval.github_pr_number, "pr_url": approval.github_pr_url, "pr_state": approval.github_pr_state, "draft": True}

    provider = GitHubWriteProvider()

    try:
        result = await provider.create_commit_and_pr(owner=owner, repo=repo, base_branch=base_branch, head_branch=branch, files=approval.proposed_files, commit_message=(
            f"fix: address incident {approval.investigation_id}"
        ), pr_title=(
            f"TraceForge: {approval.patch_summary}"
        ), pr_body=(
            "## Automated incident remediation\n\n"
            f"**Investigation:** {approval.investigation_id}\n"
            f"**Patch approval:** {approval.id}\n\n"
            "This is an AI-generated remediation proposal. "
            "Review the code and test results before merging.\n\n"
            "### Risks\n"
            + "\n".join(f"- {risk}" for risk in approval.risks)
            + "\n\n### Tests to run\n"
            + "\n".join(
                f"- {test}" for test in approval.tests_to_run
            )
        ))
        approval.github_commit_sha = result["commit_sha"]
        approval.github_pr_number = result["pr_number"]
        approval.github_pr_url = result["pr_url"]
        approval.github_pr_state = result["pr_state"]
        record_audit_event(db, action="GITHUB_PR_CREATED", outcome="SUCCESS", actor_user_id=current_user.id, resource_type="PatchApproval", resource_id=approval.id, metadata={"patch_id": approval.id, "project_id": project_id, "repository": f"{owner}/{repo}", "branch": branch, "commit_sha": approval.github_commit_sha, "pr_number": approval.github_pr_number, "pr_state": approval.github_pr_state})
        db.commit()
        return result
    except Exception:
        db.rollback()
        record_audit_event(db, action="GITHUB_PR_CREATED", outcome="FAILURE", actor_user_id=current_user.id, resource_type="PatchApproval", resource_id=approval.id, metadata={"patch_id": approval.id, "project_id": project_id, "repository": f"{owner}/{repo}", "branch": branch, "reason_code": "github_write_failed"})
        db.commit()
        raise
