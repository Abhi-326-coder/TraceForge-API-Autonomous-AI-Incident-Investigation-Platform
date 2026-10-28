
from app.evaluation.fixtures import INCIDENT_FIXTURES
from app.schemas.evaluation import EvaluationCase


EVALUATION_CASES = [
    EvaluationCase(
        case_id=case_id,
        description=fixture["incident"]["description"],
        expected_root_cause=fixture["expected_root_cause"],
        required_evidence_terms=fixture["required_evidence_terms"],
        forbidden_claims=fixture["forbidden_claims"],
    )
    for case_id, fixture in INCIDENT_FIXTURES.items()
]
