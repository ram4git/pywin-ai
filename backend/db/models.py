# win-auto/backend/db/models.py
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from db.database import Base


class ExecutionStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    stopped = "stopped"


class StepStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


def _uuid():
    return str(uuid.uuid4())


class Script(Base):
    __tablename__ = "scripts"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    plan = Column(JSON, nullable=True)
    generated_code = Column(Text, nullable=True)
    last_successful_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    executions = relationship("Execution", back_populates="script")


class Execution(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True, default=_uuid)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    plan = Column(JSON, nullable=False)
    status = Column(SAEnum(ExecutionStatus), default=ExecutionStatus.running)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    pid = Column(Integer, nullable=True)
    script = relationship("Script", back_populates="executions")
    steps = relationship("ExecutionStep", back_populates="execution", order_by="ExecutionStep.step_number")


class ExecutionStep(Base):
    __tablename__ = "execution_steps"
    id = Column(String, primary_key=True, default=_uuid)
    execution_id = Column(String, ForeignKey("executions.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    action = Column(JSON, nullable=False)
    status = Column(SAEnum(StepStatus), default=StepStatus.pending)
    screenshot_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    execution = relationship("Execution", back_populates="steps")
