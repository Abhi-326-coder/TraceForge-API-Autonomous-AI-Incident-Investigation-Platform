from app.sandbox.runner import SandboxRunner


def test_sandbox_runner_executes_python():
    runner = SandboxRunner(timeout_seconds=30)

    result = runner.run_python_tests(
        source_files={
            "test_example.py": (
                "import unittest\n"
                "\n"
                "class AdditionTests(unittest.TestCase):\n"
                "    def test_addition(self):\n"
                "        self.assertEqual(2 + 2, 4)\n"
            ),
        },
        test_command=[
            "python", "-m", "unittest", "discover", "-v"
        ],
    )

    assert result.status == "PASSED"
    assert result.exit_code == 0
    assert result.timed_out is False
    assert "Ran 1 test" in result.stderr