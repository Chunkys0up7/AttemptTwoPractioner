from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from mcp.db.base import Base

class WorkflowDefinition(Base):
    """
    SQLAlchemy model for the WorkflowDefinition table.
    Represents a workflow definition, including its steps and metadata.
    """
    __tablename__ = "workflow_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    steps = relationship("WorkflowStep", back_populates="workflow_definition", cascade="all, delete-orphan", order_by="WorkflowStep.order")
    # owner = relationship("User", back_populates="workflow_definitions")
    runs = relationship("WorkflowRun", back_populates="workflow_definition")

class WorkflowStep(Base):
    """
    SQLAlchemy model for the WorkflowStep table.
    Represents a step within a workflow, including input mappings and MCP version linkage.
    """
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_definition_id = Column(Integer, ForeignKey("workflow_definitions.id"), nullable=False)
    mcp_version_id = Column(Integer, ForeignKey("mcp_versions.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    input_mappings = Column(JSON, nullable=True, default=dict)

    workflow_definition = relationship("WorkflowDefinition", back_populates="steps")
    mcp_version = relationship("MCPVersion", back_populates="workflow_steps")
