"""
Database model for Action Logs.
"""
import uuid
from sqlalchemy import Column, String, DateTime, func, Index, JSON
# from sqlalchemy.orm import relationship # Unused

# Assuming Base is defined in mcp.db.base_class
from mcp.db.base import Base


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True),
                       default=func.now(), nullable=False)

    # Actor who performed the action. Can be a user ID, system component name, or API key ID.
    actor_id = Column(String, nullable=True, index=True)

    action_type = Column(String, nullable=False, index=True)
    # Examples: "MCP_DEFINITION_CREATED", "MCP_VERSION_UPDATED", "WORKFLOW_RUN_STARTED",
    # "WORKFLOW_STEP_STATUS_CHANGED", "USER_LOGIN_SUCCESS", "EXTERNAL_DB_CONFIG_DELETED"

    entity_type = Column(String, nullable=True, index=True)
    # Name of the primary entity this action pertains to, e.g., "MCPDefinition", "MCPVersion",
    # "WorkflowRun", "WorkflowStepInstance", "User", "ExternalDatabaseConfig"

    entity_id = Column(String, nullable=True, index=True)
    # The actual ID (UUID or other string representation) of the entity involved.
    # Using String to accommodate various ID types, though UUIDs are common in this project.

    action_metadata = Column(JSON, nullable=True)
    # Additional contextual information about the action (e.g., error details, IP address, etc.).
    # E.g., for an update: {"old_values": {...}, "new_values": {...}}
    # E.g., for a login: {"ip_address": "1.2.3.4"}
    # E.g., for an error: {"error_message": "...", "stack_trace": "..."}

    # Optional: Link to a User model if you have one and actor_id refers to it
    # user = relationship("User", foreign_keys=[actor_id], primaryjoin="User.id == ActionLog.actor_id", backref="action_logs")

    __table_args__ = (
        # Index for sorting/filtering by time
        Index('ix_action_logs_timestamp', 'timestamp'),
        # Composite indexes can be useful depending on query patterns, e.g.:
        # Index('ix_action_logs_entity_type_id', 'entity_type', 'entity_id'),
        # Index('ix_action_logs_action_type_timestamp', 'action_type', 'timestamp'),
    )

    def __repr__(self):
        return f"<ActionLog(id={self.id}, timestamp='{self.timestamp}', actor='{self.actor_id}', action='{self.action_type}', entity='{self.entity_type}:{self.entity_id}', metadata={self.action_metadata})>"
