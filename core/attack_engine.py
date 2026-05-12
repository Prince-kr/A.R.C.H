import os
import yaml
from utils.logger import Logger
from utils.executor import Executor
from utils.validator import AttackValidator

class AttackEngine:
    def __init__(self, scripts_dir: str = "scripts/red"):
        self.scripts_dir = scripts_dir
        self.executor = Executor()
        self.config = self._load_config()

    def _load_config(self):
        try:
            with open("config.yaml", "r") as f:
                return yaml.safe_load(f)
        except:
            return {"execution": {"timeout_seconds": 60}}

    def run_script(self, script_name: str, target: str, payload: str = ""):
        script_path = os.path.join(self.scripts_dir, f"{script_name}.py")
        timeout = self.config.get("execution", {}).get("timeout_seconds", 0)
        
        Logger.info(f"Executing attack: [bold red]{script_name}[/bold red] on {target}...")
        
        # Check if we should use Docker fallback (if tool not found locally)
        # This is a high-level check. Actual tool existence is checked inside the script.
        # But we can pass a 'USE_DOCKER' flag or similar.
        
        args = ["--target", target, "--payload", payload]
        stdout, status = self.executor.run_script(script_path, args, timeout=timeout)
        
        # If the script reported a FileNotFoundError (status 1 and specific message)
        if "binary not found" in stdout and os.name == 'nt':
            # Use a more robust check for container status
            check_running, _ = self.executor.run_direct_command(["docker", "inspect", "-f", "{{.State.Running}}", "arch_attacker"])
            
            if "true" not in check_running.lower():
                Logger.error("Docker container 'arch_attacker' is NOT active or running.")
                Logger.info("[yellow]Please run 'python main.py testbed up' first.[/yellow]")
                return f"Error: Docker container offline.\nDebug Info: {check_running}", 1
            
            Logger.info("[bold yellow]Tool not found on Windows. Attempting Docker Execution...[/bold yellow]")
            # Run the same python script inside the container (since /scripts is mounted)
            docker_script_path = f"/scripts/red/{script_name}.py"
            docker_cmd = ["docker", "exec", "arch_attacker", "python3", docker_script_path, "--target", target, "--payload", payload]
            stdout, status = self.executor.run_direct_command(docker_cmd, timeout=timeout)
            
        # --- NEW: Heuristic Validation ---
        is_valid, message = AttackValidator.validate(script_name, stdout)
        if not is_valid:
            Logger.warning(f"Heuristic Validation Failed: {message}")
            status = 1 # Mark as failure
            stdout = f"[!] VALIDATION ERROR: {message}\n\n{stdout}"

        # --- NEW: Auto-Map Nmap -> Exploit -> Payload ---
        if script_name == "nmap_scan" and status == 0:
            stdout += self._auto_map_nmap_to_exploit(stdout)
            
        return stdout, status

    def _auto_map_nmap_to_exploit(self, nmap_output: str) -> str:
        """Parses Nmap output and suggests Metasploit payloads based on open ports."""
        mapping = []
        if "21/tcp" in nmap_output.lower() and "open" in nmap_output.lower():
            mapping.append("Port 21 (FTP) -> Payload: 'vsftpd' (exploit/unix/ftp/vsftpd_234_backdoor)")
        if "139/tcp" in nmap_output.lower() or "445/tcp" in nmap_output.lower():
            mapping.append("Port 139/445 (SMB) -> Payload: 'samba' (exploit/linux/samba/is_known_pipename)")
        if "80/tcp" in nmap_output.lower() or "8080/tcp" in nmap_output.lower():
            mapping.append("Port 80/8080 (HTTP) -> Payload: 'apache_struts' (exploit/multi/http/struts2_content_type_ognl)")

        if mapping:
            map_str = "\n\n[+] AUTO-MAPPER: Discovered Vulnerable Services. Suggested MSF Payloads:\n"
            for m in mapping:
                map_str += f"    - {m}\n"
            return map_str
        return ""
