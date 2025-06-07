"""
Database models for Workflow Definitions and Runs with enhanced validation and monitoring.
"""
import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum as SAEnum, Index, Boolean
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from datetime import datetime
import logging

from mcp.db.base import Base
from mcp.monitoring.performance import performance_monitor

logger = logging.getLogger(__name__)

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    graph_representation = Column(JSONB, nullable=False)
    version = Column(String(50), nullable=False, default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False, default="system")
    updated_by = Column(String(255), nullable=False, default="system")
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    runs = relationship(
        "WorkflowRun", back_populates="definition", cascade="all, delete-orphan",
        order_by="desc(WorkflowRun.created_at)"
    )

    # Indexes
    __table_args__ = (
        Index('idx_workflow_name_version', 'name', 'version'),
        Index('idx_workflow_created_by', 'created_by'),
        Index('idx_workflow_updated_by', 'updated_by'),
    )

    @validates('graph_representation')
    def validate_graph(self, key, value):
        """Validate workflow graph structure."""
        try:
            # Basic validation - ensure we have nodes and edges
            if not isinstance(value, dict):
                raise ValueError("Graph representation must be a dictionary")
            if 'nodes' not in value or 'edges' not in value:
                raise ValueError("Graph must contain nodes and edges")
            
            return value
        except Exception as e:
            logger.error(f"Invalid workflow graph: {e}")
            performance_monitor.increment_error("workflow_graph_validation", str(e))
            raise

    def __repr__(self):
        return f"<WorkflowDefinition(id={self.id}, name='{self.name}', version='{self.version}')>"

class WorkflowRunStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    SUSPENDED = "SUSPENDED"

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_definition_id = Column(PG_UUID(as_uuid=True), ForeignKey(
        "workflow_definitions.id"), nullable=False, index=True)
    status = Column(SAEnum(WorkflowRunStatus, name="workflow_run_status_enum", create_type=False),
                    nullable=False, default=WorkflowRunStatus.PENDING, index=True)
    parameters = Column(JSONB, nullable=True)
    results = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
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
