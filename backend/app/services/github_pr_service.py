import hashlib
import json

from sqlalchemy.orm import Session

from app.db.models import PatchApproval
from app.providers.github_writes import GitHubWriteProvider


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
    patch_id: int,
    owner: str,
    repo: str,
    base_branch: str,
) -> dict:
    approval = db.get(PatchApproval, patch_id)

    if approval is None:
        raise ValueError("Patch approval not found")

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

    provider = GitHubWriteProvider()

    result = await provider.create_commit_and_pr(
        owner=owner,
        repo=repo,
        base_branch=base_branch,
        head_branch=branch,
        files=approval.proposed_files,
        commit_message=(
            f"fix: address incident {approval.investigation_id}"
        ),
        pr_title=(
            f"TraceForge: {approval.patch_summary}"
        ),
        pr_body=(
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
        ),
    )

    approval.github_commit_sha = result["commit_sha"]
    approval.github_pr_number = result["pr_number"]
    approval.github_pr_url = result["pr_url"]

    db.commit()

    return result