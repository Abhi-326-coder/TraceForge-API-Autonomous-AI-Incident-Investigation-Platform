
from app.schemas.evaluation import (
    EvaluationInput,
    EvaluationResult,
)


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def evaluate_case(
    evaluation: EvaluationInput,
) -> EvaluationResult:
    case = evaluation.case
    failures: list[str] = []

    predicted = normalize(evaluation.predicted_root_cause)
    expected = normalize(case.expected_root_cause)

    # Baseline exact/substring matching.
    # We can add semantic scoring later.
    root_cause_match = (
        expected in predicted or predicted in expected
    ) if predicted else False

    if not root_cause_match:
        failures.append("ROOT_CAUSE_MISMATCH")

    available_ids = {
        item.get("id")
        for item in evaluation.available_evidence
        if isinstance(item.get("id"), int)
    }

    evidence_grounded = (
        bool(evaluation.evidence_ids)
        and all(
            evidence_id in available_ids
            for evidence_id in evaluation.evidence_ids
        )
    )

    if not evidence_grounded:
        failures.append("INVALID_OR_MISSING_EVIDENCE_REFERENCE")

    evidence_text = normalize(
        " ".join(
            str(item.get("content", ""))
            for item in evaluation.available_evidence
            if item.get("id") in evaluation.evidence_ids
        )
    )

    required_terms = [
        normalize(term)
        for term in case.required_evidence_terms
    ]

    required_evidence_covered = (
        all(term in evidence_text for term in required_terms)
        if required_terms
        else True
    )

    if not required_evidence_covered:
        failures.append("REQUIRED_EVIDENCE_NOT_COVERED")

    combined_claim = normalize(
        evaluation.predicted_root_cause
        + " "
        + evaluation.explanation
    )

    forbidden_claim_detected = any(
        normalize(claim) in combined_claim
        for claim in case.forbidden_claims
        if normalize(claim)
    )

    if forbidden_claim_detected:
        failures.append("FORBIDDEN_CLAIM_DETECTED")

    # A generated remediation must not be considered safe merely
    # because an evaluation says it was approved. Production
    # approval must be enforced independently by the service.
    remediation_policy_passed = (
        not evaluation.remediation_approved
        or (
            evidence_grounded
            and not forbidden_claim_detected
        )
    )

    if not remediation_policy_passed:
        failures.append("REMEDIATION_POLICY_FAILED")

    passed = (
        root_cause_match
        and evidence_grounded
        and required_evidence_covered
        and not forbidden_claim_detected
        and remediation_policy_passed
    )

    return EvaluationResult(
        case_id=case.case_id,
        root_cause_match=root_cause_match,
        evidence_grounded=evidence_grounded,
        required_evidence_covered=required_evidence_covered,
        forbidden_claim_detected=forbidden_claim_detected,
        remediation_policy_passed=remediation_policy_passed,
        tool_calls=evaluation.tool_calls,
        duration_ms=evaluation.duration_ms,
        passed=passed,
        failures=failures,
    )
