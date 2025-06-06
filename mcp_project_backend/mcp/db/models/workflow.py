"""
Database models for Workflow Definitions and Runs.
"""
import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from datetime import datetime

from mcp.db.base import Base  # Use the Base from mcp.db.base


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    # Structure of the workflow, e.g., a list of steps, connections between them.
    # Could be a graph structure (nodes and edges) represented in JSON.
    graph_representation = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    # Relationships
    runs = relationship(
        "WorkflowRun", back_populates="definition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkflowDefinition(id={self.id}, name='{self.name}')>"


class WorkflowRunStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_definition_id = Column(PG_UUID(as_uuid=True), ForeignKey(
        "workflow_definitions.id"), nullable=False, index=True)
    status = Column(SAEnum(WorkflowRunStatus, name="workflow_run_status_enum", create_type=False),
                    nullable=False, default=WorkflowRunStatus.PENDING, index=True)
    # Parameters used for this specific run
    run_parameters = Column(JSONB, nullable=True)
    # Results or outputs of the workflow run
    results = Column(JSONB, nullable=True)
    # Logs specific to this run, could be detailed JSON or reference to a log store
    logs = Column(Text, nullable=True)  # Or JSONB for structured logs
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    # Relationships
    definition = relationship("WorkflowDefinition", back_populates="runs")
    # workflow_steps_executions = relationship("WorkflowStepExecution", back_populates="workflow_run", cascade="all, delete-orphan") # Future

    def __repr__(self):
        return f"<WorkflowRun(id={self.id}, definition_id={self.workflow_definition_id}, status='{self.status.value}')>"

# If you decide to model WorkflowStepExecution explicitly for detailed step tracking:
# class WorkflowStepExecution(Base):
#     __tablename__ = "workflow_step_executions"
#     id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     workflow_run_id = Column(PG_UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False, index=True)
#     step_id_in_graph = Column(String, nullable=False) # Identifier of the step in the WorkflowDefinition.graph_representation
#     mcp_version_id = Column(PG_UUID(as_uuid=True), ForeignKey("mcp_versions.id"), nullable=True) # Which MCPVersion was executed
#     status = Column(String(50), nullable=False) # e.g., PENDING, RUNNING, SUCCESS, FAILED
#     inputs = Column(JSONB, nullable=True)
#     outputs = Column(JSONB, nullable=True)
#     logs = Column(Text, nullable=True)
#     started_at = Column(DateTime, nullable=True)
#     ended_at = Column(DateTime, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
#     workflow_run = relationship("WorkflowRun", back_populates="workflow_steps_executions")
#     executed_mcp_version = relationship("MCPVersion")
