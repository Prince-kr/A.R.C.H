import os
import yaml
from utils.logger import Logger
from utils.executor import Executor

class DefenseEngine:
    def __init__(self, scripts_dir: str = "scripts/blue"):
        self.scripts_dir = scripts_dir
        self.executor = Executor()
        self.config = self._load_config()

    def _load_config(self):
        try:
            with open("config.yaml", "r") as f:
                return yaml.safe_load(f)
        except:
            return {"execution": {"timeout_seconds": 60}}

    def run_script(self, script_name: str, session_id: int):
        script_path = os.path.join(self.scripts_dir, f"{script_name}.py")
        timeout = self.config.get("execution", {}).get("timeout_seconds", 60)
        
        Logger.info(f"Executing defense/monitoring: [bold blue]{script_name}[/bold blue]...")
        
        args = ["--session", str(session_id)]
        return self.executor.run_script(script_path, args, timeout=timeout)
