import re

class AttackValidator:
    """
    Utility to perform heuristic validation on attack tool outputs
    to identify false positives where exit status is 0 but execution failed.
    """
    
    # Common failure patterns across various security tools
    GLOBAL_FAILURE_PATTERNS = [
        r"Usage:",
        r"invalid option",
        r"command not found",
        r"failed to connect",
        r"Connection refused",
        r"Access denied",
        r"Permission denied",
        r"Authentication failed",
        r"Module failed",
        r"Unknown command",
        r"Error:",
        r"Exception in thread",
        r"Traceback \(most recent call last\)"
    ]

    @staticmethod
    def validate(tool_name, stdout, stderr=""):
        combined_output = f"{stdout}\n{stderr}"
        
        # 1. Check for global failure patterns
        for pattern in AttackValidator.GLOBAL_FAILURE_PATTERNS:
            if re.search(pattern, combined_output, re.IGNORECASE):
                return False, f"Heuristic Match: Found failure pattern '{pattern}'"

        # 2. Tool-specific validation logic
        if tool_name == "nmap_scan":
            if "0 hosts up" in combined_output:
                return False, "Nmap reported 0 hosts up."
        
        if tool_name == "hydra_brute":
            if "0 of 0 target successfully completed" in combined_output:
                return False, "Hydra failed to target any service."
        
        if tool_name == "sqlmap_audit":
            if "all tested parameters do not appear to be injectable" in combined_output:
                # This is technically a successful scan but a failed exploit
                # Depending on the goal, we might flag it. 
                # For now, let's just stick to execution errors.
                pass

        return True, "Success"
