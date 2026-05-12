import subprocess
import os
from utils.logger import Logger

class Executor:
    def __init__(self):
        pass

    def run_script(self, script_path: str, args_list: list, timeout: int = 60):
        if not os.path.exists(script_path):
            return f"Error: Script {script_path} not found", 1

        command = ["python", script_path] + args_list
        
        try:
            # If timeout is 0 or None, run without timeout restriction
            exec_timeout = timeout if timeout and timeout > 0 else None
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=exec_timeout
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[!] Error Output:\n{result.stderr}"
            return output, result.returncode
        except subprocess.TimeoutExpired:
            return f"Timeout expired after {timeout}s", 1
    def run_direct_command(self, command: list, timeout: int = None):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout if timeout and timeout > 0 else None
            )
            # Combine stdout and stderr for full visibility
            output = result.stdout
            if result.stderr:
                output += f"\n[!] Error Output:\n{result.stderr}"
            return output, result.returncode
        except Exception as e:
            return str(e), 1
