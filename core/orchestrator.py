from core.attack_engine import AttackEngine
from core.defense_engine import DefenseEngine
from database.repository import Repository
from utils.logger import Logger

class Orchestrator:
    def __init__(self):
        self.attack_engine = AttackEngine()
        self.defense_engine = DefenseEngine()
        self.repo = Repository()

    def run_sequential_cycle(self, attack_tool: str, target: str, payload: str, defense_tool: str):
        Logger.info("Starting Sequential Attack-Defense Cycle...")
        
        # 1. Ensure testbed exists
        testbed = self.repo.get_latest_testbed()
        if not testbed:
            testbed = self.repo.create_testbed("Default Lab", "192.168.100.0/24")

        # 2. Create Session
        session = self.repo.create_session(testbed.id)
        Logger.info(f"Session Created: ID {session.id}")

        # 3. Attack Phase
        stdout, status = self.attack_engine.run_script(attack_tool, target, payload)
        attack_log = self.repo.log_attack(session.id, attack_tool, target, payload, stdout, status)
        Logger.attack(f"Attack Logged. Exit Status: {status}")

        # 4. Defense Phase
        findings, def_status = self.defense_engine.run_script(defense_tool, session.id)
        self.repo.log_defense(session.id, attack_log.id, defense_tool, findings)
        Logger.defend(f"Defense Telemetry Collected. Status: {def_status}")

        Logger.success(f"Cycle Complete. Data committed to 'data/purple_team.db'")
        return session.id

    def run_standalone_attack(self, tool: str, target: str, payload: str):
        testbed = self.repo.get_latest_testbed() or self.repo.create_testbed("Default Lab", "192.168.100.0/24")
        session = self.repo.create_session(testbed.id, mode="attack_only")
        stdout, status = self.attack_engine.run_script(tool, target, payload)
        self.repo.log_attack(session.id, tool, target, payload, stdout, status)
        return session.id, stdout, status

    def run_standalone_defense(self, tool: str, session_id: str):
        testbed = self.repo.get_latest_testbed() or self.repo.create_testbed("Default Lab", "192.168.100.0/24")
        # For standalone defense, we might be checking an existing session or creating a new audit one
        actual_session_id = session_id
        if session_id == "latest" or session_id == "realtime_monitor":
            db_session = self.repo.create_session(testbed.id, mode="defense_only")
            actual_session_id = db_session.id
            
        findings, status = self.defense_engine.run_script(tool, actual_session_id)
        # Log it as a defense record. If it's a new session, attack_log_id might be null (None)
        self.repo.log_defense(actual_session_id, None, tool, findings)
        return actual_session_id, findings, status
