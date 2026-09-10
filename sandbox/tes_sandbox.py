# from runner import DockerSandboxRunner
# from schemas import CodeExecutionRequest

# if __name__ == "__main__":
#     runner = DockerSandboxRunner()
    
#     # Simple code check
#     payload = CodeExecutionRequest(
#         code="import os; print(f'Running as UID: {os.getuid()}'); print('Sandbox execution successful!')"
#     )
    
#     result = runner.execute_code(payload)
#     print("--- EXECUTION RESULT ---")
#     print(f"Exit Code: {result.exit_code}")
#     print(f"Stdout:\n{result.stdout}")
#     print(f"Stderr:\n{result.stderr}")
#     print(f"Runtime: {result.execution_time_seconds}s")

from guardrails.sanitizer import CodeSanitizer

if __name__ == "__main__":
    # Test 1: Malicious network payload
    bad_code = "import socket\ns = socket.socket()\ns.connect(('1.1.1.1', 80))"
    is_safe, violations = CodeSanitizer.inspect_code(bad_code)
    print("Test 1 - Malicious Code:")
    print(f"Is Safe: {is_safe} | Violations: {violations}\n")

    # Test 2: Safe data transformation code
    good_code = "data = [1, 2, 3]\nprint(sum(data))"
    is_safe, violations = CodeSanitizer.inspect_code(good_code)
    print("Test 2 - Safe Code:")
    print(f"Is Safe: {is_safe} | Violations: {violations}")