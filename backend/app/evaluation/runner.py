
from app.evaluation.cases import EVALUATION_CASES
from app.evaluation.fixtures import INCIDENT_FIXTURES
from app.schemas.evaluation import EvaluationInput
from app.services.evaluation_service import (
    evaluate_case,
    summarize_results,
)


def run_fixture_evaluations() -> dict:
    results = []

    for case in EVALUATION_CASES:
        fixture = INCIDENT_FIXTURES[case.case_id]

        # Baseline only: use the expected answer as a synthetic
        # prediction to verify evaluator and dataset plumbing.
        # This is NOT a measurement of agent performance.
        evidence = [
            {
                "id": entry["id"],
                "content": entry["message"],
            }
            for entry in fixture["logs"]
        ]

        input_data = EvaluationInput(
            case=case,
            predicted_root_cause=case.expected_root_cause,
            explanation="Synthetic baseline for evaluator validation.",
            evidence_ids=[
                entry["id"] for entry in evidence
            ],
            available_evidence=evidence,
            tool_calls=0,
            duration_ms=0,
        )

        results.append(evaluate_case(input_data))

    return {
        "summary": summarize_results(results),
        "results": [
            result.model_dump()
            for result in results
        ],
        "mode": "synthetic_evaluator_smoke_test",
    }


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            run_fixture_evaluations(),
            indent=2,
        )
    )
