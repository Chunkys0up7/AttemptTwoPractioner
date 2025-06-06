"""
Service layer for creating audit log entries (ActionLog).
"""
# import uuid # Unused
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
# Not strictly needed if relying on DB default for timestamp
# from datetime import datetime # Unused

from mcp.db.models.action_log import ActionLog


class AuditingService:
    def __init__(self, db: Session):
        """
        Initializes the AuditingService with a database session.

        Args:
            db: The SQLAlchemy Session to use for database operations.
        """
        self.db = db

    def create_action_log_entry(
        self,
        *,  # Make all arguments keyword-only for clarity
        actor_id: Optional[str] = None,
        action_type: str,
        entity_type: Optional[str] = None,
        # Can be str or UUID, stored as str in model
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        commit: bool = True  # Flag to control commit, useful if called within a larger transaction
    ) -> ActionLog:
        """
        Creates and saves a new action log entry.

        Args:
            actor_id: Identifier for the user or system component performing the action.
            action_type: Type of action performed (e.g., "MCP_CREATED", "WORKFLOW_EXECUTED").
            entity_type: The type of entity primarily affected by the action (e.g., "MCPVersion").
            entity_id: The ID of the entity primarily affected.
            details: A dictionary containing any additional context or data about the action.
            commit: If True, commits the session after adding the log. 
                    Set to False if managing transaction externally.

        Returns:
            The created ActionLog database object.
        """
        if entity_id is not None and not isinstance(entity_id, str):
            # Ensure entity_id is string if it's passed (e.g. a UUID object)
            entity_id = str(entity_id)

        log_entry = ActionLog(
            actor_id=actor_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
            # timestamp is handled by DB default (server_default=func.now() in model)
        )
        self.db.add(log_entry)

        if commit:
            try:
                self.db.commit()
                self.db.refresh(log_entry)
            except Exception as e:
                self.db.rollback()
                # Log the error appropriately
                # Basic print for now
                print(f"Error committing ActionLog entry: {e}")
                raise  # Re-raise the exception after rollback
        else:
            # If not committing here, the caller is responsible.
            # We might flush to get ID if needed, but refresh won't work without commit.
            # Flush to assign ID if default is client-side, or to prepare for commit by caller
            self.db.flush()
            # self.db.refresh(log_entry) # Cannot refresh if not committed and ID is server-generated

        return log_entry

# Example Usage (conceptual, would be in other services or API routers):
# async def some_api_endpoint_that_creates_mcp(
#     ...,
#     current_user_id: str = Depends(get_current_user_id), # Example auth dependency
#     db: Session = Depends(get_db)
# ):
#   # ... logic to create mcp_version ...
#   mcp_version = ...
#   try:
#       auditing_service = AuditingService(db)
#       auditing_service.create_action_log_entry(
#           actor_id=current_user_id,
#           action_type="MCP_VERSION_CREATED",
#           entity_type="MCPVersion",
#           entity_id=str(mcp_version.id),
#           details={"name": mcp_version.name, "type": mcp_version.mcp_type},
#           commit=False # Assuming outer transaction commits this with MCP creation
#       )
#       # ... other operations ...
#       db.commit() # Commit both MCP creation and log entry
#   except Exception as e:
#       db.rollback()
#       raise HTTPException(status_code=500, detail="Failed to create MCP and log action.")
#   return mcp_version
