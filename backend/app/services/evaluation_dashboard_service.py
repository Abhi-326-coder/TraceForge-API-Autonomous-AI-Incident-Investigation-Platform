from app.evaluation.runner import run_fixture_evaluations


def get_evaluation_dashboard() -> dict:
    report = run_fixture_evaluations()

    summary = report["summary"]
    results = report["results"]

    total = len(results)

    return {
        "mode": report["mode"],
        "total_cases": total,
        "passed_cases": summary.get("passed_cases", 0),
        "failed_cases": summary.get("failed_cases", 0),
        "pass_rate": summary.get("pass_rate", 0.0),
        "root_cause_accuracy": summary.get(
            "root_cause_accuracy", 0.0
        ),
        "evidence_grounding_rate": summary.get(
            "evidence_grounding_rate", 0.0
        ),
        "average_duration_ms": summary.get(
            "average_duration_ms", 0.0
        ),
        "average_tool_calls": summary.get(
            "average_tool_calls", 0.0
        ),
        "cases": [
            {
                "case_id": result["case_id"],
                "passed": result["passed"],
                "root_cause_match": result["root_cause_match"],
                "evidence_grounded": result["evidence_grounded"],
                "required_evidence_covered": result[
                    "required_evidence_covered"
                ],
                "forbidden_claim_detected": result[
                    "forbidden_claim_detected"
                ],
                "failures": result["failures"],
            }
            for result in results
        ],
    }