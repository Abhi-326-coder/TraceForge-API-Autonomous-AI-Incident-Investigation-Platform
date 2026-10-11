import re

from sqlalchemy.orm import Session

from app.db.models import PatchApproval
from app.providers.github_rest import GitHubRESTProvider


async def create_branch_for_approval(
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

    provider = GitHubRESTProvider()

    return await provider.create_branch(
        owner=owner,
        repo=repo,
        base_branch=base_branch,
        new_branch=branch_name,
    )