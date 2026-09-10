import ast
import re
from typing import List, Tuple

class SecurityViolationError(Exception):
    """Raised when user/LLM generated code violates sandbox security rules."""
    pass

class CodeSanitizer:
    """Raised when LLM-generated code or input prompts violate security rules."""

    BLOCKED_PROMPT_KEYWORDS = {
        "subprocess",
        "socket",
        "ctypes",
        "/etc/passwd",
        "docker.sock",
        "rm -rf",
        "eval(",
        "exec(",
        "os.system",
        "threading",
        "pty",
        "shutil",
        "signal",
        "multiprocessing",
    }

    # Banned Built-in Functions & Magic Attributes
    BLOCKED_BUILTINS = {"eval", "exec", "__import__", "compile", "breakpoint"}

    SUSPICIOUS_PATTERNS = [
        re.compile(r"os\.environ\[?.*\]?"),  # Environment variable dumping
        re.compile(r"\/proc\/"),  # Accessing Linux process info
        re.compile(r"\/sys\/"),  # Accessing system kernel interfaces
        re.compile(r"rm\s+-rf"),  # Destructive recursive deletion
        re.compile(r"\/var\/run\/docker\.sock"),
    ]

    @classmethod
    def inspect_code(cls, code: str) -> Tuple[bool, List[str]]:
        violations: List[str] = []

        # A. Pre-flight raw string keyword check (Catches natural language prompts & imports)
        lower_code = code.lower()
        for kw in cls.BLOCKED_PROMPT_KEYWORDS:
            if kw in lower_code:
                violations.append(
                    f"Forbidden security keyword or pattern detected: '{kw}'"
                )

        # B. Regex pre-check for blocked patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if pattern.search(code):
                violations.append(
                    f"Forbidden security pattern detected: '{pattern.pattern}'"
                )

        # C. AST structural check for builtins and reflection reflection attributes
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check for banned function calls: `eval(...)`
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id in cls.BLOCKED_BUILTINS
                ):
                    violations.append(
                        f"Forbidden builtin function call: '{node.func.id}()'"
                    )

                # Check for dangerous attribute access like `__subclasses__` or `__builtins__`
                elif isinstance(node, ast.Attribute) and node.attr in {
                    "__subclasses__",
                    "__builtins__",
                    "__globals__",
                }:
                    violations.append(
                        f"Forbidden reflection attribute access: '{node.attr}'"
                    )

        except SyntaxError:
            # If it's pure natural language text that failed regex/keyword checks, ignore AST parse failures
            pass

        is_safe = len(violations) == 0
        return is_safe, violations

    @classmethod
    def validate_or_raise(cls, code: str) -> None:
        """Convenience method that raises SecurityViolationError if code is unsafe."""
        is_safe, violations = cls.inspect_code(code)
        if not is_safe:
            violation_str = "; ".join(violations)
            raise SecurityViolationError(
                f"Security Guardrail Interception: {violation_str}"
            )

    @classmethod
    def validate_or_raise(cls, code: str) -> None:
        """Convenience method that raises SecurityViolationError if code is unsafe."""
        is_safe, violations = cls.inspect_code(code)
        if not is_safe:
            violation_str = "; ".join(violations)
            raise SecurityViolationError(f"Security Guardrail Interception: {violation_str}")