from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime, Enum as DBEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from mcp.db.base import Base
from enum import Enum

class WorkflowRunStatusEnum(str, Enum):
    """
    Enum for workflow run status, matching frontend and Pydantic types.
    """
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"
    ABORTED = "Aborted"

class WorkflowRun(Base):
    """
    SQLAlchemy model for the WorkflowRun table.
    Tracks the execution of a workflow, including status, inputs, outputs, and timing.
    """
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_definition_id = Column(Integer, ForeignKey("workflow_definitions.id"), nullable=False)
    status = Column(DBEnum(WorkflowRunStatusEnum, name="workflow_run_status"), nullable=False, default=WorkflowRunStatusEnum.PENDING, index=True)
    initial_inputs = Column(JSON, nullable=True)
    final_outputs = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    triggered_by_actor_id = Column(String, nullable=True)

    workflow_definition = relationship("WorkflowDefinition", back_populates="runs")
    # Optionally, add step logs/events as a relationship or JSON field
