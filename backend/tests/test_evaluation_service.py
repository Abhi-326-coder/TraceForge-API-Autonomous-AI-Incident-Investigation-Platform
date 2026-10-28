
from app.schemas.evaluation import (
    EvaluationCase,
    EvaluationInput,
)
from app.services.evaluation_service import evaluate_case


def test_correct_root_cause_with_real_evidence():
    case = EvaluationCase(
        case_id="test-001",
        description="Checkout returns HTTP 500.",
        expected_root_cause="database connection pool exhaustion",
        required_evidence_terms=[
            "database connection pool exhausted"
        ],
    )

    evaluation = EvaluationInput(
        case=case,
        predicted_root_cause=(
            "Database connection pool exhaustion"
        ),
        explanation="The logs show the database connection pool exhausted.",
        evidence_ids=[1],
        available_evidence=[
            {
                "id": 1,
                "content": (
                    "ERROR: Database connection pool exhausted"
                ),
            }
        ],
        tool_calls=2,
        duration_ms=850,
    )

    result = evaluate_case(evaluation)

    assert result.root_cause_match is True
    assert result.evidence_grounded is True
    assert result.required_evidence_covered is True
    assert result.passed is True


def test_rejects_fabricated_evidence_id():
    case = EvaluationCase(
        case_id="test-002",
        description="Test fabricated evidence.",
        expected_root_cause="database connection pool exhaustion",
    )

    evaluation = EvaluationInput(
        case=case,
        predicted_root_cause="database connection pool exhaustion",
        evidence_ids=[999],
        available_evidence=[
            {"id": 1, "content": "Database pool exhausted"}
        ],
    )

    result = evaluate_case(evaluation)

    assert result.evidence_grounded is False
    assert result.passed is False
    assert "INVALID_OR_MISSING_EVIDENCE_REFERENCE" in result.failures


def test_detects_forbidden_claim():
    case = EvaluationCase(
        case_id="test-003",
        description="Unsupported security claim.",
        expected_root_cause="database connection pool exhaustion",
        forbidden_claims=["confirmed malicious attack"],
    )

    evaluation = EvaluationInput(
        case=case,
        predicted_root_cause="database connection pool exhaustion",
        explanation="This is a confirmed malicious attack.",
        evidence_ids=[1],
        available_evidence=[
            {"id": 1, "content": "Database connection pool exhausted"}
        ],
    )

    result = evaluate_case(evaluation)

    assert result.forbidden_claim_detected is True
    assert result.passed is False
