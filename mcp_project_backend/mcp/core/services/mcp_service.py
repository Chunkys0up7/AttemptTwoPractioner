"""
Service layer for MCPDefinition and MCPVersion CRUD operations.

This module contains the business logic for managing MCP entities, interacting
with the database via SQLAlchemy models.
"""
import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException

from mcp.db.models import MCPDefinition, MCPVersion
from mcp.schemas.mcp import MCPDefinitionCreate, MCPDefinitionUpdate, MCPVersionCreate, MCPVersionUpdate
from mcp.db.models.external_db_config import ExternalDatabaseConfig
from mcp.core.services.auditing_service import AuditingService


class MCPService:
    def __init__(self, db: Session):
        self.db = db
        self.auditing_service = AuditingService(
            db)  # Initialize AuditingService

    # --- MCPDefinition CRUD ---
    def create_mcp_definition(self, mcp_def_create: MCPDefinitionCreate, actor_id: Optional[str] = None) -> MCPDefinition:
        """Creates a new MCPDefinition, optionally with an initial version."""
        # Check for existing name
        existing_def = self.db.query(MCPDefinition).filter(
            MCPDefinition.name == mcp_def_create.name).first()
        if existing_def:
            raise ValueError(
                f"MCPDefinition with name '{mcp_def_create.name}' already exists.")

        db_mcp_def = MCPDefinition(
            name=mcp_def_create.name,
            description=mcp_def_create.description
        )
        self.db.add(db_mcp_def)
        self.db.flush()  # Flush to get the ID for the version if needed

        initial_version_details = None
        if mcp_def_create.initial_version:
            # Ensure the version's mcp_type matches the config's inner type if provided
            if mcp_def_create.initial_version.config and \
               mcp_def_create.initial_version.mcp_type != mcp_def_create.initial_version.config.type:
                raise ValueError(
                    f"MCPVersion mcp_type '{mcp_def_create.initial_version.mcp_type}' does not match "
                    f"config.type '{mcp_def_create.initial_version.config.type}'."
                )

            # external_db_config_ids validation for initial version
            if mcp_def_create.initial_version.external_db_config_ids:
                for db_id_str in mcp_def_create.initial_version.external_db_config_ids:
                    # type: ignore
                    if not self.db.query(ExternalDatabaseConfig).filter(ExternalDatabaseConfig.id == uuid.UUID(db_id_str)).first():
                        raise HTTPException(
                            status_code=404, detail=f"ExternalDatabaseConfig with id {db_id_str} not found for initial version.")

            db_initial_version = MCPVersion(
                mcp_definition_id=db_mcp_def.id,
                # version_string=mcp_def_create.initial_version.version_string, # Assuming version_string is replaced by name/number
                name=mcp_def_create.initial_version.name or f"{db_mcp_def.name} v1",
                version_number=1,  # Initial version is 1
                description=mcp_def_create.initial_version.description,
                mcp_type=mcp_def_create.initial_version.mcp_type,
                config=mcp_def_create.initial_version.config,
                external_db_config_ids=[str(
                    uid) for uid in mcp_def_create.initial_version.external_db_config_ids] if mcp_def_create.initial_version.external_db_config_ids else []
            )
            self.db.add(db_initial_version)
            initial_version_details = {
                "id": str(db_initial_version.id), "name": db_initial_version.name}

        # Log action before commit
        self.auditing_service.create_action_log_entry(
            actor_id=actor_id,
            action_type="MCP_DEFINITION_CREATED",
            entity_type="MCPDefinition",
            entity_id=str(db_mcp_def.id),
            details={"name": db_mcp_def.name, "description": db_mcp_def.description, "initial_version_created": bool(
                initial_version_details), "initial_version_details": initial_version_details},
            commit=False  # Commit will be done after all operations
        )

        self.db.commit()
        self.db.refresh(db_mcp_def)
        if initial_version_details:  # Refresh initial version if created
            self.db.refresh(db_initial_version)
        return db_mcp_def

    def get_mcp_definition(self, mcp_def_id: uuid.UUID) -> Optional[MCPDefinition]:
        """Retrieves an MCPDefinition by its ID, including its versions."""
        return (
            self.db.query(MCPDefinition)
            # Efficiently load versions
            .options(selectinload(MCPDefinition.versions))
            .filter(MCPDefinition.id == mcp_def_id)
            .first()
        )

    def get_mcp_definition_by_name(self, name: str) -> Optional[MCPDefinition]:
        """Retrieves an MCPDefinition by its unique name, including its versions."""
        return (
            self.db.query(MCPDefinition)
            .options(selectinload(MCPDefinition.versions))
            .filter(MCPDefinition.name == name)
            .first()
        )

    def list_mcp_definitions(self, skip: int = 0, limit: int = 100) -> Tuple[List[MCPDefinition], int]:
        """Lists MCPDefinitions with pagination."""
        query = self.db.query(MCPDefinition).options(
            selectinload(MCPDefinition.versions))
        total = query.count()  # Get total count before applying limit/offset
        definitions = query.offset(skip).limit(limit).all()
        return definitions, total

    def update_mcp_definition(
        self, mcp_def_id: uuid.UUID, mcp_def_update: MCPDefinitionUpdate, actor_id: Optional[str] = None
    ) -> Optional[MCPDefinition]:
        """Updates an existing MCPDefinition."""
        db_mcp_def = self.get_mcp_definition(
            mcp_def_id)  # Fetches with versions
        if not db_mcp_def:
            return None

        old_values = {"name": db_mcp_def.name,
                      "description": db_mcp_def.description}
        update_data = mcp_def_update.model_dump(exclude_unset=True)
        changes_made = False
        if "name" in update_data and update_data["name"] != db_mcp_def.name:
            # Check if new name conflicts with another definition
            existing_def = self.db.query(MCPDefinition).filter(
                MCPDefinition.name == update_data["name"]).first()
            if existing_def:
                raise ValueError(
                    f"MCPDefinition with name '{update_data['name']}' already exists.")
            db_mcp_def.name = update_data["name"]
            changes_made = True

        if "description" in update_data and db_mcp_def.description != update_data["description"]:
            db_mcp_def.description = update_data["description"]
            changes_made = True

        if changes_made:
            self.auditing_service.create_action_log_entry(
                actor_id=actor_id,
                action_type="MCP_DEFINITION_UPDATED",
                entity_type="MCPDefinition",
                entity_id=str(mcp_def_id),
                details={"old_values": old_values, "new_values": {
                    "name": db_mcp_def.name, "description": db_mcp_def.description}},
                commit=False
            )
            self.db.commit()
            self.db.refresh(db_mcp_def)
        return db_mcp_def

    def delete_mcp_definition(self, mcp_def_id: uuid.UUID, actor_id: Optional[str] = None) -> bool:
        """Deletes an MCPDefinition and its associated versions (due to cascade)."""
        db_mcp_def = self.db.query(MCPDefinition).filter(
            MCPDefinition.id == mcp_def_id).first()
        if not db_mcp_def:
            return False

        # Log before delete
        self.auditing_service.create_action_log_entry(
            actor_id=actor_id,
            action_type="MCP_DEFINITION_DELETED",
            entity_type="MCPDefinition",
            entity_id=str(mcp_def_id),
            details={"name": db_mcp_def.name},
            commit=False
        )
        self.db.delete(db_mcp_def)
        self.db.commit()
        return True

    # --- MCPVersion CRUD (within a Definition) ---
    def create_mcp_version(self, definition_id: uuid.UUID, version_create: MCPVersionCreate, actor_id: Optional[str] = None) -> MCPVersion:
        mcp_definition = self.get_mcp_definition(definition_id)
        if not mcp_definition:
            # Or a custom exception
            raise HTTPException(
                status_code=404, detail="MCPDefinition not found")

        # Validate external_db_config_ids
        if version_create.external_db_config_ids:
            for db_config_id in version_create.external_db_config_ids:
                db_config = self.db.query(ExternalDatabaseConfig).filter(
                    ExternalDatabaseConfig.id == db_config_id).first()
                if not db_config:
                    raise HTTPException(
                        status_code=404, detail=f"ExternalDatabaseConfig with id {db_config_id} not found")

        latest_version = self.db.query(MCPVersion)\
            .filter(MCPVersion.mcp_definition_id == definition_id)\
            .order_by(MCPVersion.version_number.desc())\
            .first()

        new_version_number = (
            latest_version.version_number + 1) if latest_version else 1

        db_mcp_version = MCPVersion(
            mcp_definition_id=definition_id,
            version_number=new_version_number,
            # Default name
            name=version_create.name or f"{mcp_definition.name} v{new_version_number}",
            description=version_create.description,
            mcp_type=version_create.mcp_type,  # Set from MCPVersionCreate
            # config is handled by the hybrid property setter using version_create.config
            external_db_config_ids=[str(
                uid) for uid in version_create.external_db_config_ids] if version_create.external_db_config_ids else []
        )
        # The config setter will handle config_payload_data and potentially mcp_type alignment
        db_mcp_version.config = version_create.config

        # If mcp_type was changed by config setter, ensure it matches the input if strict
        # Or, rely on the config setter to be the source of truth for mcp_type if it's derived.
        # Current MCPVersion model setter updates self.mcp_type from new_config.type
        # So, db_mcp_version.mcp_type will reflect config.type after the assignment above.

        self.db.add(db_mcp_version)

        self.auditing_service.create_action_log_entry(
            actor_id=actor_id,
            action_type="MCP_VERSION_CREATED",
            entity_type="MCPVersion",
            # ID available after add if client-side default, or after flush
            entity_id=str(db_mcp_version.id),
            details={
                "name": db_mcp_version.name,
                "version_number": db_mcp_version.version_number,
                "mcp_type": db_mcp_version.mcp_type,
                "mcp_definition_id": str(definition_id)
            },
            commit=False
        )
        self.db.commit()
        self.db.refresh(db_mcp_version)
        return db_mcp_version

    def get_mcp_version(self, version_id: uuid.UUID) -> Optional[MCPVersion]:
        return self.db.query(MCPVersion).filter(MCPVersion.id == version_id).first()

    def get_mcp_versions_for_definition(self, definition_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[MCPVersion]:
        return self.db.query(MCPVersion)\
            .filter(MCPVersion.mcp_definition_id == definition_id)\
            .order_by(MCPVersion.version_number.desc())\
            .offset(skip).limit(limit).all()

    def update_mcp_version(self, version_id: uuid.UUID, version_update: MCPVersionUpdate, actor_id: Optional[str] = None) -> Optional[MCPVersion]:
        db_mcp_version = self.get_mcp_version(version_id)
        if not db_mcp_version:
            return None

        old_values = {
            "name": db_mcp_version.name,
            "description": db_mcp_version.description,
            "mcp_type": db_mcp_version.mcp_type,
            # Potentially log old config summary or hash, full config might be too large
            # "config_summary": str(db_mcp_version.config.model_dump(exclude_none=True))[:200] if db_mcp_version.config else None,
            "external_db_config_ids": db_mcp_version.external_db_config_ids
        }
        update_data = version_update.model_dump(exclude_unset=True)
        changes_made = False

        # Validate external_db_config_ids if provided in update_data
        if "external_db_config_ids" in update_data and update_data["external_db_config_ids"] is not None:
            for db_config_id in update_data["external_db_config_ids"]:
                # Ensure db_config_id is a valid UUID if they are stored as UUID objects in the list
                # If they are strings, this check is fine.
                db_config = self.db.query(ExternalDatabaseConfig).filter(
                    ExternalDatabaseConfig.id == db_config_id).first()
                if not db_config:
                    raise HTTPException(
                        status_code=404, detail=f"ExternalDatabaseConfig with id {db_config_id} not found")
            # Convert UUIDs to strings if storing as list of strings
            new_ids = [str(uid)
                       for uid in update_data["external_db_config_ids"]]
            if db_mcp_version.external_db_config_ids != new_ids:
                db_mcp_version.external_db_config_ids = new_ids
                changes_made = True
        elif "external_db_config_ids" in update_data and update_data["external_db_config_ids"] is None:
            db_mcp_version.external_db_config_ids = []  # Explicitly set to empty list
            changes_made = True

        if "config" in update_data and update_data["config"] is not None:
            # Use the hybrid property setter
            db_mcp_version.config = update_data["config"]
            # The setter in MCPVersion model also updates mcp_type based on config.type
            if "mcp_type" in update_data and db_mcp_version.mcp_type != update_data["mcp_type"]:
                # This case implies a mismatch if mcp_type is also explicitly in update_data
                # and differs from what config.type implies.
                # The Pydantic schema validator for MCPVersionUpdate should ideally catch this.
                # Or, decide on precedence (e.g., config.type overrules mcp_type in payload).
                # Assuming config.type takes precedence via the model's setter.
                pass
            # Prevent direct assignment to config_payload_data
            del update_data["config"]

        # Update mcp_type separately if it's in update_data and not handled by config setter
        # (e.g. if config is not being updated, but mcp_type is changing for a no-config component)
        if "mcp_type" in update_data and db_mcp_version.mcp_type != update_data["mcp_type"] and not ("config" in update_data and update_data["config"] is not None):
            db_mcp_version.mcp_type = update_data["mcp_type"]
            changes_made = True

        # Apply other updates
        for field, value in update_data.items():
            if hasattr(db_mcp_version, field) and getattr(db_mcp_version, field) != value:
                setattr(db_mcp_version, field, value)
                changes_made = True

        if changes_made:
            new_values = {
                "name": db_mcp_version.name,
                "description": db_mcp_version.description,
                "mcp_type": db_mcp_version.mcp_type,
                "external_db_config_ids": db_mcp_version.external_db_config_ids
            }
            self.auditing_service.create_action_log_entry(
                actor_id=actor_id,
                action_type="MCP_VERSION_UPDATED",
                entity_type="MCPVersion",
                entity_id=str(version_id),
                details={"old_values": old_values, "new_values": new_values},
                commit=False
            )
            self.db.commit()
            self.db.refresh(db_mcp_version)
        return db_mcp_version

    def delete_mcp_version(self, version_id: uuid.UUID, actor_id: Optional[str] = None) -> bool:
        """Deletes an MCPVersion."""
        db_mcp_version = self.get_mcp_version(version_id)
        if not db_mcp_version:
            return False

        self.auditing_service.create_action_log_entry(
            actor_id=actor_id,
            action_type="MCP_VERSION_DELETED",
            entity_type="MCPVersion",
            entity_id=str(version_id),
            details={"name": db_mcp_version.name, "version_number": db_mcp_version.version_number,
                     "mcp_definition_id": str(db_mcp_version.mcp_definition_id)},
            commit=False
        )
        self.db.delete(db_mcp_version)
        self.db.commit()
        return True

    # Note: Update/Delete for MCPVersion might be restricted depending on versioning strategy.
    # For example, versions might be immutable once created.
    # Add update/delete for MCPVersion if needed, similar to MCPDefinition.
    # def update_mcp_version(...)
    # def delete_mcp_version(...)
