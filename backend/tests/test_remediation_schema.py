from app.schemas.remediation import (
    RemediationProposal,
    ProposedChange
)

def test_remediation_proposal_schema():
    proposal = RemediationProposal(
        title="Investigate database pool exhaustion",
        summary=(
            "Determine why database connections are being "
            "exhausted before selecting a permanent fix."
        ),
        change_type="investigation_required",
        risk="LOW",
        affected_files=[],
        proposed_changes=[
            ProposedChange(
                file_path=None,
                description=(
                    "Inspect connection acquisition and release."
                ),
                rationale=(
                    "The available evidence indicates pool exhaustion, "
                    "but does not establish its underlying cause."
                ),
            )
        ],
        test_plan=[
            "Reproduce concurrent checkout requests.",
            "Observe active and idle database connections.",
            "Verify connections are released after requests complete.",
        ],
        evidence_ids=[1],
        rollback_plan=(
            "No production change has been made; "
            "there is nothing to roll back."
        ),
        assumptions=[],
        uncertainty=(
            "The current evidence does not establish whether "
            "the cause is a connection leak or excessive concurrency."
        ),
    )

    assert proposal.risk == "LOW"
    assert proposal.evidence_ids == [1]
    assert proposal.affected_files == []