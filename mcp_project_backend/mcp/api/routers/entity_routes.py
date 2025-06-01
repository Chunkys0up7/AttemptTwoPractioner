"""
API Endpoints for fetching details of various entities in a unified way.
"""
import uuid
from enum import Enum
from typing import Union, Any, Optional # Type is unused

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
# from pydantic import BaseModel # BaseModel is unused

from mcp.db.session import get_db
from mcp.core.config import settings

# Import relevant Pydantic Read schemas and Service classes
from mcp.schemas.mcp import MCPVersionRead, MCPDefinitionRead
# Renamed to avoid conflict
from mcp.schemas.workflow import WorkflowRunRead, WorkflowDefinitionRead as WorkflowDefReadSchema
from mcp.schemas.external_db_config import ExternalDbConfigRead

from mcp.core.services.mcp_service import MCPService
# Assuming a WorkflowService exists or will be created
# from mcp.core.services.workflow_service import WorkflowService # Unused and redefined later
from mcp.core.services.external_db_config_service import ExternalDbConfigService

# Define an Enum for supported entity types


class EntityType(str, Enum):
    MCP_DEFINITION = "mcp_definition"
    MCP_VERSION = "mcp_version"
    WORKFLOW_DEFINITION = "workflow_definition"
    WORKFLOW_RUN = "workflow_run"
    EXTERNAL_DB_CONFIG = "external_db_config"
    # Add other entity types as needed


# Union of all possible Read schemas for the response_model
AnyEntityRead = Union[
    MCPDefinitionRead,
    MCPVersionRead,
    WorkflowDefReadSchema,
    WorkflowRunRead,
    ExternalDbConfigRead
]

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/entities",
    tags=["Entities"],
)

@router.get("/{entity_type}/{entity_id}", response_model=AnyEntityRead)
async def get_entity_details(
    entity_type: EntityType = Path(...,
                                   description="The type of the entity to fetch."),
    entity_id: uuid.UUID = Path(...,
                                description="The unique ID of the entity to fetch."),
    # Direct DB session for more control or specific service calls
    db: Session = Depends(get_db)
):
    """
    Fetch details for any supported entity by its type and ID.

    The response model will vary based on the `entity_type` provided.
    """
    item: Optional[Any] = None

    if entity_type == EntityType.MCP_DEFINITION:
        service = MCPService(db)
        item = service.get_mcp_definition(mcp_def_id=entity_id)
    elif entity_type == EntityType.MCP_VERSION:
        service = MCPService(db)
        item = service.get_mcp_version(version_id=entity_id)
    elif entity_type == EntityType.WORKFLOW_RUN:
        # Assuming WorkflowEngineService has a method to get run details by ID
        # from mcp.core.workflow_engine_service import WorkflowEngineService # Potentially circular if main imports this
        # For now, let's assume a get_workflow_run method in a WorkflowService
        # Placeholder until WorkflowService is fully fleshed out.
        try:
            # Try to import if exists
            from mcp.core.services.workflow_service import WorkflowService
            wf_service = WorkflowService(db)
            # Requires get_workflow_run in WorkflowService
            item = wf_service.get_workflow_run(run_id=entity_id)
        except ImportError:
            # Fallback or temporary direct query if WorkflowService is not ready
            from mcp.db.models.workflow import WorkflowRun
            item = db.query(WorkflowRun).filter(
                WorkflowRun.id == entity_id).first()
            if item:
                item = WorkflowRunRead.model_validate(
                    item)  # Ensure Pydantic model
    elif entity_type == EntityType.WORKFLOW_DEFINITION:
        try:
            # Try to import if exists
            from mcp.core.services.workflow_service import WorkflowService
            wf_service = WorkflowService(db)
            item = wf_service.get_workflow_definition(
                definition_id=entity_id)  # Requires get_workflow_definition
        except ImportError:
            from mcp.db.models.workflow import WorkflowDefinition
            item = db.query(WorkflowDefinition).filter(
                WorkflowDefinition.id == entity_id).first()
            if item:
                item = WorkflowDefReadSchema.model_validate(item)
    elif entity_type == EntityType.EXTERNAL_DB_CONFIG:
        service = ExternalDbConfigService(db)
        item = service.get_external_db_config(config_id=entity_id)
    else:
        # This case should ideally be caught by the Path validation for EntityType enum
        raise HTTPException(
            status_code=400, detail=f"Unsupported entity type: {entity_type.value}")

    if item is None:
        raise HTTPException(
            status_code=404, detail=f"{entity_type.value.replace('_', ' ').title()} with ID {entity_id} not found.")

    # Pydantic should handle the correct response model serialization from the Union AnyEntityRead
    return item

# Note: The `get_entity_service` dependency is not used in the endpoint above as it became complex
# to map service methods dynamically for this example. A direct if/else in the route is simpler for now.
# A more robust solution for many entity types might involve a registry pattern for services and their methods.

# If this file previously contained direct data retrieval logic, import and use the new data_service instead.
# from mcp.api.services.data_service import router as data_service_router
# router.include_router(data_service_router, prefix="/data", tags=["data"])
