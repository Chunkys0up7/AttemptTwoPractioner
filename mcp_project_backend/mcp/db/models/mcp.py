"""
Database models for MCP Definitions and Versions.
"""
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import Optional, Dict, Any

from mcp.db.base import Base
from mcp.core.mcp_configs import MCPConfigPayload, parse_mcp_config


class MCPDefinition(Base):
    __tablename__ = "mcp_definitions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        default=func.now(), onupdate=func.now())

    versions = relationship("MCPVersion", back_populates="mcp_definition",
                            cascade="all, delete-orphan", order_by="MCPVersion.version_number.desc()")


class MCPVersion(Base):
    __tablename__ = "mcp_versions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcp_definition_id = Column(PG_UUID(as_uuid=True), ForeignKey(
        "mcp_definitions.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    mcp_type = Column(String, nullable=False)
    config_payload_data = Column(JSONB, nullable=True)

    # New field to store a list of ExternalDatabaseConfig IDs
    external_db_config_ids = Column(JSONB, nullable=True, default=lambda: [])

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        default=func.now(), onupdate=func.now())

    mcp_definition = relationship("MCPDefinition", back_populates="versions")

    @hybrid_property
    def config(self) -> Optional[MCPConfigPayload]:
        if self.config_payload_data is None:
            return None
        # Ensure mcp_type is available for parsing
        # It should be inherently part of the class instance (self.mcp_type)
        return parse_mcp_config(self.config_payload_data, self.mcp_type)

    @config.setter
    def config(self, new_config: Optional[MCPConfigPayload]):
        if new_config is None:
            self.config_payload_data = None
        else:
            # if hasattr(new_config, 'type') and self.mcp_type != new_config.type:
            #     raise ValueError(f"MCPVersion.mcp_type ('{self.mcp_type}') and new_config.type ('{new_config.type}') mismatch.")
            self.config_payload_data = new_config.model_dump(by_alias=True)
            # Automatically set mcp_type from the config object if possible, ensuring consistency
            if hasattr(new_config, 'type'):
                self.mcp_type = new_config.type

    @classmethod
    def create_new_version(cls, db, *, mcp_definition_id: uuid.UUID, version_data: Dict[str, Any]):
        # Simplified version creation logic, assuming version_data is a dict from a Pydantic model
        latest_version = db.query(cls).filter(
            cls.mcp_definition_id == mcp_definition_id).order_by(cls.version_number.desc()).first()
        new_version_number = (
            latest_version.version_number + 1) if latest_version else 1

        mcp_version = cls(**version_data)  # type: ignore
        mcp_version.mcp_definition_id = mcp_definition_id
        mcp_version.version_number = new_version_number

        # Ensure config setter logic is triggered if 'config' is in version_data
        if 'config' in version_data and version_data['config'] is not None:
            # The Pydantic model for creation should handle parsing this into MCPConfigPayload
            # For direct dict assignment, ensure it's compatible or use the setter
            mcp_version.config = version_data['config']  # Triggers the setter
        elif 'config_payload_data' in version_data and mcp_version.mcp_type:
            # If raw payload is given, ensure mcp_type is also set to allow parsing.
            # This path is less ideal than providing a full config object.
            pass

        db.add(mcp_version)
        db.commit()
        db.refresh(mcp_version)
        return mcp_version
