"""
Database models for Workflow Definitions and Runs with enhanced validation and monitoring.
"""
import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum as SAEnum, Index, Boolean, JSON
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime, timezone
import logging
from typing import Optional, Dict, Any, List, Union
from mcp.db.base import Base
from mcp.monitoring.performance import performance_monitor

logger = logging.getLogger(__name__)

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    graph_representation = Column(JSON, nullable=False)
    version = Column(String(50), nullable=False, default="1.0.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)
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

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    workflow_definition_id = Column(String(36), ForeignKey(
        "workflow_definitions.id"), nullable=False, index=True)
    status = Column(SAEnum(WorkflowRunStatus, name="workflow_run_status_enum", create_type=False),
                    nullable=False, default=WorkflowRunStatus.PENDING, index=True)
    parameters = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Relationships
    definition = relationship("WorkflowDefinition", back_populates="runs")

    def __repr__(self):
        return f"<WorkflowRun(id={self.id}, definition_id={self.workflow_definition_id}, status='{self.status.value}')>"

class WorkflowStepExecution(Base):
    __tablename__ = "workflow_step_executions"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(String(36), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    step_id_in_graph = Column(String, nullable=False) # Identifier of the step in the WorkflowDefinition.graph_representation
    mcp_version_id = Column(String(36), ForeignKey("mcp_versions.id"), nullable=True) # Which MCPVersion was executed
    status = Column(String(50), nullable=False) # e.g., PENDING, RUNNING, SUCCESS, FAILED
    inputs = Column(JSON, nullable=True)
    outputs = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    workflow_run = relationship("WorkflowRun", backref="workflow_steps_executions")
    executed_mcp_version = relationship("MCPVersion")
