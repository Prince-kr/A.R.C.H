from database.connection import get_session
from database.models import ExecutionSession, AttackLog, DefenseTelemetry, Testbed
from sqlalchemy import desc

class Repository:
    @staticmethod
    def create_session(testbed_id: int, mode: str = "sequential"):
        session = get_session()
        try:
            db_session = ExecutionSession(testbed_id=testbed_id, mode=mode)
            session.add(db_session)
            session.commit()
            session.refresh(db_session)
            return db_session
        finally:
            session.close()

    @staticmethod
    def log_attack(session_id: int, tool: str, target: str, payload: str, stdout: str, exit_status: int):
        session = get_session()
        try:
            log = AttackLog(
                session_id=session_id,
                tool_used=tool,
                target_ip=target,
                payload=payload,
                stdout=stdout,
                exit_status=exit_status
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
        finally:
            session.close()

    @staticmethod
    def log_defense(session_id: int, attack_log_id: int, tool: str, findings: str, mitigation: str = None):
        session = get_session()
        try:
            telemetry = DefenseTelemetry(
                session_id=session_id,
                attack_log_id=attack_log_id,
                tool_used=tool,
                findings=findings,
                mitigation_action=mitigation
            )
            session.add(telemetry)
            session.commit()
            session.refresh(telemetry)
            return telemetry
        finally:
            session.close()

    @staticmethod
    def get_latest_testbed():
        session = get_session()
        try:
            testbed = session.query(Testbed).order_by(desc(Testbed.id)).first()
            return testbed
        finally:
            session.close()
            
    @staticmethod
    def create_testbed(name: str, config: str):
        session = get_session()
        try:
            testbed = Testbed(name=name, network_config=config, status="active")
            session.add(testbed)
            session.commit()
            session.refresh(testbed)
            return testbed
        finally:
            session.close()
    @staticmethod
    def get_full_knowledge_record():
        session = get_session()
        try:
            from database.models import ExecutionSession, AttackLog, DefenseTelemetry
            sessions = session.query(ExecutionSession).all()
            data = []
            for s in sessions:
                attacks = session.query(AttackLog).filter_by(session_id=s.id).all()
                defenses = session.query(DefenseTelemetry).filter_by(session_id=s.id).all()
                
                data.append({
                    "session_id": s.id,
                    "timestamp": str(s.start_time),
                    "mode": s.mode,
                    "attacks": [{
                        "tool": a.tool_used,
                        "target": a.target_ip,
                        "status": a.exit_status,
                        "stdout": a.stdout
                    } for a in attacks],
                    "defenses": [{
                        "tool": d.tool_used,
                        "findings": d.findings,
                        "mitigation": d.mitigation_action
                    } for d in defenses]
                })
            return data
        finally:
            session.close()

    @staticmethod
    def get_all_sessions():
        session = get_session()
        try:
            return session.query(ExecutionSession).order_by(desc(ExecutionSession.id)).all()
        finally:
            session.close()

    @staticmethod
    def get_session_details(session_id: int):
        import json
        session = get_session()
        try:
            s = session.query(ExecutionSession).filter_by(id=session_id).first()
            if not s: return None
            
            attack = session.query(AttackLog).filter_by(session_id=s.id).first()
            defense = session.query(DefenseTelemetry).filter_by(session_id=s.id).first()
            
            try:
                findings = json.loads(defense.findings) if defense and defense.findings.startswith("[") else defense.findings if defense else []
            except json.JSONDecodeError:
                findings = defense.findings if defense else []

            return {
                "id": s.id,
                "timestamp": str(s.start_time),
                "mode": s.mode,
                "attack": {
                    "tool": attack.tool_used if attack else "N/A",
                    "target": attack.target_ip if attack else "N/A",
                    "status": attack.exit_status if attack else "N/A",
                    "stdout": attack.stdout if attack else ""
                },
                "defense": {
                    "tool": defense.tool_used if defense else "N/A",
                    "findings": findings
                }
            }
        finally:
            session.close()
