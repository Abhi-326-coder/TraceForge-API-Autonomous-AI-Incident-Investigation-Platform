

from app.evaluation.cases import EVALUATION_CASES
from app.evaluation.fixtures import INCIDENT_FIXTURES


def test_every_fixture_has_an_evaluation_case():
    case_ids = {case.case_id for case in EVALUATION_CASES}

    assert case_ids == set(INCIDENT_FIXTURES.keys())


def test_fixture_ids_are_unique():
    case_ids = [case.case_id for case in EVALUATION_CASES]

    assert len(case_ids) == len(set(case_ids))


def test_fixtures_have_required_fields():
    for case_id, fixture in INCIDENT_FIXTURES.items():
        assert fixture["incident"]["service"]
        assert fixture["logs"]
        assert fixture["expected_root_cause"]

        assert "metrics" in fixture
        assert "required_evidence_terms" in fixture
        assert "forbidden_claims" in fixture


def test_insufficient_evidence_case_exists():
    cases = {
        case.case_id: case
        for case in EVALUATION_CASES
    }

    case = cases["checkout-insufficient-evidence-003"]

    assert (
        case.expected_root_cause
        == "insufficient evidence to determine root cause"
    )
