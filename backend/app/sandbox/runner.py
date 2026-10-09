import subprocess
import tempfile
import time

from datetime import datetime, timezone
from pathlib import Path

from app.schemas.sandbox import SandboxResult


# Pin the image to a digest for stronger reproducibility in production.
# This tag is convenient for the initial local prototype.
SANDBOX_IMAGE = "python:3.12-slim"


class SandboxRunner:
    def __init__(
        self,
        timeout_seconds: int = 60,
        memory_limit: str = "256m",
        cpu_limit: str = "1",
    ):
        self.timeout_seconds = timeout_seconds
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit

    def run_python_tests(
        self,
        source_files: dict[str, str],
        test_command: list[str],
    ) -> SandboxResult:
        if not source_files:
            raise ValueError("Sandbox workspace cannot be empty")

        # Never accept an arbitrary shell string from an LLM.
        # This initial runner only permits pytest or unittest.
        if test_command not in (
            ["python", "-m", "pytest", "-q"],
            ["python", "-m", "unittest", "discover", "-v"],
        ):
            raise ValueError("Test command is not allowlisted")

        started_at = datetime.now(timezone.utc)
        start = time.monotonic()

        with tempfile.TemporaryDirectory(
            prefix="traceforge-sandbox-"
        ) as temporary_dir:
            workspace = Path(temporary_dir).resolve()

            for relative_path, content in source_files.items():
                path = Path(relative_path)

                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or not path.parts
                ):
                    raise ValueError(
                        f"Unsafe workspace path: {relative_path}"
                    )

                destination = (workspace / path).resolve()

                if not destination.is_relative_to(workspace):
                    raise ValueError(
                        f"Path escapes workspace: {relative_path}"
                    )

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                destination.write_text(
                    content,
                    encoding="utf-8",
                )

            command = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", self.memory_limit,
                "--cpus", self.cpu_limit,
                "--pids-limit", "64",
                "--read-only",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges",
                "--user", "65534:65534",
                "--mount",
                f"type=bind,src={workspace},dst=/workspace,rw",
                "--workdir", "/workspace",
                SANDBOX_IMAGE,
                *test_command,
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )

                exit_code = result.returncode
                stdout = result.stdout[-12000:]
                stderr = result.stderr[-12000:]
                timed_out = False

                status = "PASSED" if exit_code == 0 else "FAILED"

            except subprocess.TimeoutExpired as exc:
                exit_code = None
                stdout = self._to_text(exc.stdout)[-12000:]
                stderr = self._to_text(exc.stderr)[-12000:]
                timed_out = True
                status = "TIMED_OUT"

            except OSError as exc:
                exit_code = None
                stdout = ""
                stderr = str(exc)[:12000]
                timed_out = False
                status = "FAILED"

        completed_at = datetime.now(timezone.utc)

        return SandboxResult(
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=round(time.monotonic() - start, 3),
            timed_out=timed_out,
            started_at=started_at,
            completed_at=completed_at,
        )

    @staticmethod
    def _to_text(value) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)