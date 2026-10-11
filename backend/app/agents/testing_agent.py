from app.schemas.sandbox import SandboxResult
from app.schemas.test_report import TestReport, TestFinding


class TestingAgent:
    """Classify sandbox outcomes without relying on an LLM."""

    def evaluate(self, result: SandboxResult) -> TestReport:
        output = f"{result.stdout}\n{result.stderr}".strip()
        output_lower = output.lower()

        findings = []
        actions = []
        limitations = []

        if result.timed_out or result.status == "TIMED_OUT":
            status = "INCONCLUSIVE"

            findings.append(
                TestFinding(
                    category="timeout",
                    title="Test execution timed out",
                    explanation=(
                        "The sandbox did not finish within its time limit. "
                        "The patch has not been validated."
                    ),
                    relevant_output=output[-3000:],
                )
            )

            actions.append(
                "Inspect the test output and rerun with an appropriate "
                "timeout if the test suite is expected to take longer."
            )

        elif result.exit_code is None:
            status = "INCONCLUSIVE"

            findings.append(
                TestFinding(
                    category="environment_failure",
                    title="Test execution could not be confirmed",
                    explanation=(
                        "No process exit code was produced. "
                        "The test outcome cannot be established."
                    ),
                    relevant_output=output[-3000:],
                )
            )

            actions.append(
                "Inspect Docker availability, image startup, and "
                "sandbox configuration."
            )

        elif result.exit_code == 0:
            status = "PASSED"

            actions.append(
                "Review test coverage and run additional integration "
                "or regression tests where appropriate."
            )

        else:
            # An exit code alone does not prove whether the cause
            # was application code, missing dependencies, or setup.
            environment_markers = [
                "modulenotfounderror",
                "no module named",
                "command not found",
                "could not find a version that satisfies",
                "permission denied",
                "no such file or directory",
            ]

            environment_failure = any(
                marker in output_lower
                for marker in environment_markers
            )

            status = (
                "INCONCLUSIVE"
                if environment_failure
                else "FAILED"
            )

            findings.append(
                TestFinding(
                    category=(
                        "environment_failure"
                        if environment_failure
                        else "test_failure"
                    ),
                    title=(
                        "Possible test environment problem"
                        if environment_failure
                        else "Test command failed"
                    ),
                    explanation=(
                        "The output contains signs of an environment "
                        "or dependency issue. Fix the environment and "
                        "rerun before judging the patch."
                        if environment_failure
                        else
                        "The test command exited unsuccessfully. "
                        "Inspect the output to identify the cause."
                    ),
                    relevant_output=output[-3000:],
                )
            )

            actions.append(
                "Inspect the failing output, correct the identified "
                "problem, and rerun the tests."
            )

        if not output:
            limitations.append(
                "The sandbox returned no stdout or stderr. "
                "The report cannot identify individual failing tests."
            )

        return TestReport(
            status=status,
            exit_code=result.exit_code,
            duration_seconds=result.duration_seconds,
            summary=self._summary(status),
            findings=findings,
            recommended_actions=actions,
            tests_executed=True,
            limitations=limitations,
        )

    @staticmethod
    def _summary(status: str) -> str:
        return {
            "PASSED": (
                "The configured test command exited successfully. "
                "This does not prove the patch is production-safe."
            ),
            "FAILED": (
                "The configured test command failed. "
                "The output requires investigation."
            ),
            "INCONCLUSIVE": (
                "The test result is inconclusive. "
                "Resolve the execution or environment issue first."
            ),
        }[status]