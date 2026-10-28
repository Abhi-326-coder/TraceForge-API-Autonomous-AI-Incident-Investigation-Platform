
from app.schemas.evaluation import EvaluationCase


EVALUATION_CASES = [
    EvaluationCase(
        case_id="checkout-db-pool-001",
        description=(
            "Checkout returns HTTP 500 errors while the "
            "database connection pool is exhausted."
        ),
        expected_root_cause=(
            "database connection pool exhaustion"
        ),
        required_evidence_terms=[
            "database connection pool exhausted",
            "98",
        ],
        forbidden_claims=[
            "confirmed malicious attack",
            "database permanently destroyed",
        ],
    ),
    EvaluationCase(
        case_id="checkout-unknown-002",
        description=(
            "Checkout errors occur, but available evidence "
            "does not establish the root cause."
        ),
        expected_root_cause=(
            "insufficient evidence to determine root cause"
        ),
        required_evidence_terms=[],
        forbidden_claims=[
            "definitely caused by a database outage",
        ],
    ),
]
