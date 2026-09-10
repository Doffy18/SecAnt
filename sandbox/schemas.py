from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class sandbox_config(BaseModel):
    "sandbox configurations and isolation settings"
    image: str = Field(default="python:3.12-alpine", description="Docker image tag to execute against")
    mem_limit: str = Field(default="512m", description="Maximum memory allocation (e.g., '512m', '1g')")
    nano_cpus: int = Field(default=1_000_000_000, description="CPU ceiling in nanoseconds (1_000_000_000 = 1 CPU core)")
    timeout_seconds: int = Field(default=10, description="Execution timeout limit before hard termination")
    network_disabled: bool = Field(default=True, description="Enforce strict network isolation")
    read_only_root: bool = Field(default=True, description="Mount root filesystem as read-only")
    user: str = Field(default="nobody", description="Unprivileged execution user (UID 65534)")

class CodeExecutionRequest(BaseModel):
    """Payload representing a single code execution request."""
    code: str = Field(..., description="Python source code to execute")
    config: sandbox_config = Field(default_factory=sandbox_config, description="Isolation parameters")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Non-sensitive environment variables") 

class ExecutionResult(BaseModel):
    """Output metrics and logs captured from container execution."""
    stdout: str = Field(default="", description="Standard output logs")
    stderr: str = Field(default="", description="Standard error logs")
    exit_code: int = Field(default=0, description="Process return status code (0 = success)")
    execution_time_seconds: float = Field(..., description="Total wall-clock runtime in seconds")
    timed_out: bool = Field(default=False, description="Flag indicating if the process exceeded timeout limits")
    error_message: Optional[str] = Field(default=None, description="System or engine error message if container setup failed")
