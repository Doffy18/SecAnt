from sandbox.schemas import CodeExecutionRequest, sandbox_config 
from mcp.server.mcpserver import MCPServer
from sandbox.runner import DockerSandboxRunner
from typing import Dict, Any

mcp = MCPServer("SecAnt Execution Server")
runner = DockerSandboxRunner()


@mcp.tool()
def code_execute(code: str) -> dict:
    """Executes Python source code securely inside an isolated, non-root ephemeral Docker sandbox."""
    payload = CodeExecutionRequest(code=code)
    result = runner.execute_code(payload)
    output_dict = result.model_dump()
    output_dict["executed_code"] = code  # Attach executed code to tool result
    return output_dict


if __name__ == "__main__":
    mcp.run(transport="stdio")