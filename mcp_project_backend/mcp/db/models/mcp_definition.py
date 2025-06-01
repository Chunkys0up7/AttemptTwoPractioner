from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from mcp.db.base import Base

class MCPDefinition(Base):
    """
    SQLAlchemy model for the MCPDefinition table.
    Represents a definition of an MCP, including its type, tags, and versions.
    """
    __tablename__ = "mcp_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    mcp_type = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    versions = relationship("MCPVersion", back_populates="definition", cascade="all, delete-orphan")
    # owner = relationship("User", back_populates="mcp_definitions")

class MCPVersion(Base):
    """
    SQLAlchemy model for the MCPVersion table.
    Represents a version of an MCP, including its config payload and linkage to definition.
    """
    __tablename__ = "mcp_versions"

    id = Column(Integer, primary_key=True, index=True)
    mcp_definition_id = Column(Integer, ForeignKey("mcp_definitions.id"), nullable=False)
    version_string = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    mcp_type = Column(String, nullable=False)
    config_payload_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # is_latest = Column(Boolean, default=False, index=True)

    definition = relationship("MCPDefinition", back_populates="versions")
    workflow_steps = relationship("WorkflowStep", back_populates="mcp_version")
