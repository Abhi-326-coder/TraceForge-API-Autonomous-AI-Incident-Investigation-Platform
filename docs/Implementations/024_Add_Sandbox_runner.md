## Add Sandbox Environment runner and test to run the runner

### First creating the schema what our Sandbox is going to return or we are expecting

```python
class SandboxResult(BaseModel):
    status: str
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    started_at: datetime
    completed_at: datetime
```

### Now I need a SandboxRunner class which will have a function called "runner" which will create an restricted or condensed environment to test our code 

- A class called ``SandboxRunner`` having ``run_python_tests`` is created and in which environment for source file be created and tests will be ran

```python
    def run_python_tests(
        self,
        source_files: dict[str, str],
        test_command: list[str],
    ) -> SandboxResult:
```

- Using the tempfile module to create a temperary folder by name or prefix in which the source file will be created and using docker the file is tested 

```python
with tempfile.TemporaryDirectory(
            prefix="traceforge-sandbox-"
        ) as temporary_dir:
```

- Creating a command, which will create the docker container and within an SANDBOX_IMAGE = "python:3.12-slim" and python test will be ran under this environment 

```python
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
```

-  Using the subprocess to run above command and testing under the created docker environment or container 

- tested the sandbox runner under test_sandbox_runnder.py 