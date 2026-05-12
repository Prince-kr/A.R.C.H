from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Testbed(Base):
    __tablename__ = "testbed"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    network_config = Column(String)
    status = Column(String, default="offline")

class ExecutionSession(Base):
    __tablename__ = "execution_session"
    id = Column(Integer, primary_key=True)
    testbed_id = Column(Integer, ForeignKey("testbed.id"))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    mode = Column(String)

class AttackLog(Base):
    __tablename__ = "attack_log"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, index=True)
    tool_used = Column(String)
    target_ip = Column(String)
    payload = Column(String)
    stdout = Column(String, nullable=True)
    exit_status = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

class DefenseTelemetry(Base):
    __tablename__ = "defense_telemetry"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, index=True)
    attack_log_id = Column(Integer)
    tool_used = Column(String)
    findings = Column(String)
    mitigation_action = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)
