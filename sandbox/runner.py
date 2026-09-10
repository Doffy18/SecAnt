import time
import docker
from docker.errors import APIError, ContainerError, ImageNotFound
from sandbox.schemas import CodeExecutionRequest, ExecutionResult, sandbox_config
from sandbox.guardrails.sanitizer import CodeSanitizer, SecurityViolationError
from sandbox.guardrails.en_filter import EnvironmentFilter

class DockerSandboxRunner:
    "handles highly restricted docker container execution"

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise RuntimeError(f"failed to connect to docker daemon: {e}")

    def execute_code(self, request: CodeExecutionRequest) -> ExecutionResult:
        "runs python code in a shortlived container and collects logs"

        is_safe, violations = CodeSanitizer.inspect_code(request.code)
        if not is_safe:
            return ExecutionResult(
                stdout="",
                stderr="\n".join(violations),
                exit_code=126,  # Command invoked cannot execute / blocked
                execution_time_seconds=0.0,
                error_message="Execution blocked by SecAnt Pre-Flight Security Guardrail"
            )

        # 2. Environment scrubbing
        sanitized_env = EnvironmentFilter.sanitize(request.environment or {})
        request.environment = sanitized_env


        config: sandbox_config = request.config
        start_time = time.time()

        command = ['python', '-c', request.code]
        try:
            # 1. Create container
            container = self.client.containers.create(
                image=config.image,
                command=command,
                network_disabled=config.network_disabled,
                mem_limit=config.mem_limit,
                nano_cpus=config.nano_cpus,
                user=config.user,
                read_only=config.read_only_root,
                tmpfs={"/tmp": "rw,size=64M,exec"},
                environment=request.environment or {}
            )

            try:
                # 2. Start container
                container.start()

                # 3. Wait for process completion
                result = container.wait(timeout=config.timeout_seconds)
                exit_code = result.get("StatusCode", 0)

                # 4. Read stdout and stderr separately from container logs
                stdout_bytes = container.logs(stdout=True, stderr=False)
                stderr_bytes = container.logs(stdout=False, stderr=True)

            finally:
                # 5. Guaranteed container cleanup
                container.remove(force=True)

            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout=(stdout_bytes or b"").decode("utf-8", errors="replace"),
                stderr=(stderr_bytes or b"").decode("utf-8", errors="replace"),
                exit_code=exit_code,
                execution_time_seconds=round(execution_time, 4),
                timed_out=False
            )

        except ImageNotFound:
            return ExecutionResult(
                stdout="",
                stderr="",
                exit_code=1,
                execution_time_seconds=round(time.time() - start_time, 4),
                error_message=f"Docker image '{config.image}' not found locally. Please pull the image."
            )

        except APIError as api_err:
            return ExecutionResult(
                stdout="",
                stderr="",
                exit_code=1,
                execution_time_seconds=round(time.time() - start_time, 4),
                error_message=f"Docker Engine API Error: {api_err.explanation}"
            )