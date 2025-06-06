from sqlalchemy.orm import Session
from .base_crud import CRUDBase
from mcp.db.models.mcp_definition import MCPDefinition, MCPVersion
from mcp.api.schemas.mcp_definition_schemas import MCPDefinitionCreate, MCPDefinitionUpdate
from mcp.api.schemas.mcp_version_schemas import MCPVersionCreate, MCPVersionUpdate
from typing import Optional, List

class CRUDMCPDefinition(CRUDBase[MCPDefinition, MCPDefinitionCreate, MCPDefinitionUpdate]):
    """
    CRUD operations for the MCPDefinition model.
    Inherits generic CRUD operations from CRUDBase.
    """
    def create(self, db: Session, *, obj_in: MCPDefinitionCreate, owner_id: Optional[int] = None) -> MCPDefinition:
        """
        Create an MCPDefinition.
        Args:
            db (Session): SQLAlchemy session.
            obj_in (MCPDefinitionCreate): Data for the MCP definition.
            owner_id (Optional[int]): Owner ID if applicable.
        Returns:
            MCPDefinition: The created MCPDefinition instance.
        """
        db_obj_data = obj_in.model_dump()
        # if owner_id:
        #     db_obj_data["owner_id"] = owner_id
        db_obj = self.model(**db_obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Add any specific query methods for MCPDefinition here
    # def get_by_name(self, db: Session, *, name: str) -> Optional[MCPDefinition]:
    #     return db.query(self.model).filter(self.model.name == name).first()

class CRUDMCPVersion(CRUDBase[MCPVersion, MCPVersionCreate, MCPVersionUpdate]):
    """
    CRUD operations for the MCPVersion model, including creation with definition linkage.
    Inherits generic CRUD operations from CRUDBase.
    """
    def create_with_definition(self, db: Session, *, obj_in: MCPVersionCreate, definition_id: int) -> MCPVersion:
        """
        Create an MCPVersion linked to a specific MCPDefinition.
        Args:
            db (Session): SQLAlchemy session.
            obj_in (MCPVersionCreate): Data for the MCP version.
            definition_id (int): ID of the parent MCPDefinition.
        Returns:
            MCPVersion: The created MCPVersion instance.
        """
        db_obj_data = obj_in.model_dump(exclude={"config"})
        db_obj = self.model(**db_obj_data, mcp_definition_id=definition_id)
        # Set the config using the property setter, which handles serialization
        db_obj.config = obj_in.config
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Add any specific query methods for MCPVersion here
    # def get_versions_for_definition(self, db: Session, *, definition_id: int, skip: int = 0, limit: int = 100) -> List[MCPVersion]:
    #     return db.query(self.model).filter(self.model.mcp_definition_id == definition_id).offset(skip).limit(limit).all()

crud_mcp_definition = CRUDMCPDefinition(MCPDefinition)
crud_mcp_version = CRUDMCPVersion(MCPVersion)
