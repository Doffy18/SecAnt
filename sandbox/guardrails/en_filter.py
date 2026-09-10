from typing import Dict, Set


class EnvironmentFilter:
    """Filters sensitive host system secrets before launching container environments."""

    # Key names that should never leak into sandbox environments
    SENSITIVE_KEYWORDS = {
        "SECRET", "TOKEN", "PASSWORD", "KEY", "AUTH", 
        "AWS", "GOOGLE", "OPENAI", "DATABASE", "PRIVATE"
    }

    @classmethod
    def sanitize(cls, env_vars: Dict[str, str]) -> Dict[str, str]:
        """
        Filters out any key matching sensitive security patterns.
        Returns a sanitized environment dictionary.
        """
        if not env_vars:
            return {}

        clean_env: Dict[str, str] = {}
        
        for key, value in env_vars.items():
            key_upper = key.upper()
            
            # Drop keys matching blocked security terms
            if any(keyword in key_upper for keyword in cls.SENSITIVE_KEYWORDS):
                continue
                
            clean_env[key] = value

        return clean_env