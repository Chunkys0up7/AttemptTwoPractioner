"""
API Endpoints for fetching details of various entities in a unified way.
"""
import uuid
from enum import Enum
from typing import Union, Any, Optional, List # Type is unused

from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from sqlalchemy.orm import Session
# from pydantic import BaseModel # BaseModel is unused

from mcp.db.session import get_db
from mcp.core.config import settings

# Import relevant Pydantic Read schemas and Service classes
from mcp.schemas.mcp import MCPVersionRead, MCPDefinitionRead, MCPDefinitionCreate, MCPDefinitionUpdate, MCPVersionCreate, MCPVersionUpdate
# Renamed to avoid conflict
from mcp.schemas.workflow import WorkflowRunRead, WorkflowDefinitionRead as WorkflowDefReadSchema, WorkflowDefinitionCreate, WorkflowRunCreate
from mcp.schemas.external_db_config import ExternalDbConfigRead

from mcp.core.services.mcp_service import MCPService
# Assuming a WorkflowService exists or will be created
# from mcp.core.services.workflow_service import WorkflowService # Unused and redefined later
from mcp.core.services.external_db_config_service import ExternalDbConfigService

from mcp.db.models.workflow import WorkflowDefinition, WorkflowRun
from mcp.schemas.workflow import WorkflowDefinitionRead
from sqlalchemy.exc import IntegrityError

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

DUMMY_ACTOR_ID = "system_actor_placeholder_uuid"

# --- MCPDefinition CRUD ---

@router.post("/mcp-definitions/", response_model=MCPDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_mcp_definition(
    mcp_def_create: MCPDefinitionCreate = Body(...),
    db: Session = Depends(get_db)
):
    service = MCPService(db)
    try:
        db_mcp_def = service.create_mcp_definition(mcp_def_create=mcp_def_create, actor_id=DUMMY_ACTOR_ID)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error creating MCP Definition: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during MCP Definition creation.")
    return MCPDefinitionRead.model_validate(db_mcp_def)

@router.get("/mcp-definitions/", response_model=List[MCPDefinitionRead])
def list_mcp_definitions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = MCPService(db)
    defs, _ = service.list_mcp_definitions(skip=skip, limit=limit)
    return [MCPDefinitionRead.model_validate(d) for d in defs]

@router.get("/mcp-definitions/{definition_id}", response_model=MCPDefinitionRead)
def get_mcp_definition(definition_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MCPService(db)
    db_mcp_def = service.get_mcp_definition(definition_id)
    if db_mcp_def is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPDefinition not found")
    return MCPDefinitionRead.model_validate(db_mcp_def)

@router.put("/mcp-definitions/{definition_id}", response_model=MCPDefinitionRead)
def update_mcp_definition(definition_id: uuid.UUID, mcp_def_update: MCPDefinitionUpdate = Body(...), db: Session = Depends(get_db)):
    service = MCPService(db)
    try:
        updated_def = service.update_mcp_definition(mcp_def_id=definition_id, mcp_def_update=mcp_def_update, actor_id=DUMMY_ACTOR_ID)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error updating MCP Definition {definition_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during MCP Definition update.")
    if updated_def is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPDefinition not found")
    return MCPDefinitionRead.model_validate(updated_def)

@router.delete("/mcp-definitions/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mcp_definition(definition_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MCPService(db)
    try:
        deleted = service.delete_mcp_definition(mcp_def_id=definition_id, actor_id=DUMMY_ACTOR_ID)
    except Exception as e:
        print(f"Error deleting MCP Definition {definition_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during MCP Definition deletion.")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPDefinition not found")
    return

# --- MCPVersion CRUD ---

@router.post("/mcp-definitions/{definition_id}/versions/", response_model=MCPVersionRead, status_code=status.HTTP_201_CREATED)
def create_mcp_version(definition_id: uuid.UUID, version_create: MCPVersionCreate = Body(...), db: Session = Depends(get_db)):
    service = MCPService(db)
    try:
        db_mcp_version = service.create_mcp_version(definition_id=definition_id, version_create=version_create, actor_id=DUMMY_ACTOR_ID)
    except HTTPException as http_exc:
        raise http_exc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error creating MCP Version for definition {definition_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during MCP Version creation.")
    if db_mcp_version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPDefinition not found to create version for.")
    return MCPVersionRead.model_validate(db_mcp_version)

@router.get("/mcp-definitions/{definition_id}/versions/", response_model=List[MCPVersionRead])
def list_mcp_versions(definition_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = MCPService(db)
    versions = service.get_mcp_versions_for_definition(definition_id, skip=skip, limit=limit)
    return [MCPVersionRead.model_validate(v) for v in versions]

@router.get("/mcp-definitions/{definition_id}/versions/{version_id}", response_model=MCPVersionRead)
def get_mcp_version(definition_id: uuid.UUID, version_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MCPService(db)
    version = service.get_mcp_version(version_id)
    if version is None or version.mcp_definition_id != definition_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPVersion not found for this definition")
    return MCPVersionRead.model_validate(version)

@router.put("/mcp-definitions/{definition_id}/versions/{version_id}", response_model=MCPVersionRead)
def update_mcp_version(definition_id: uuid.UUID, version_id: uuid.UUID, version_update: MCPVersionUpdate = Body(...), db: Session = Depends(get_db)):
    service = MCPService(db)
    try:
        updated_version = service.update_mcp_version(version_id=version_id, version_update=version_update, actor_id=DUMMY_ACTOR_ID)
    except HTTPException as http_exc:
        raise http_exc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error updating MCP Version {version_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during MCP Version update.")
    if updated_version is None or updated_version.mcp_definition_id != definition_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPVersion not found for this definition")
    return MCPVersionRead.model_validate(updated_version)

@router.delete("/mcp-definitions/{definition_id}/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mcp_version(definition_id: uuid.UUID, version_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MCPService(db)
    try:
        deleted = service.delete_mcp_version(version_id=version_id, actor_id=DUMMY_ACTOR_ID)
    except Exception as e:
        print(f"Error deleting MCP Version {version_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during MCP Version deletion.")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCPVersion not found or already deleted")
    return

# --- WorkflowDefinition CRUD ---

@router.post("/workflow-definitions/", response_model=WorkflowDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_workflow_definition(wf_def_create: WorkflowDefinitionCreate = Body(...), db: Session = Depends(get_db)):
    try:
        wf_def = WorkflowDefinition(
            name=wf_def_create.name,
            description=wf_def_create.description,
            graph_representation=wf_def_create.definition_dsl or {},
        )
        db.add(wf_def)
        db.commit()
        db.refresh(wf_def)
        return WorkflowDefinitionRead.model_validate(wf_def)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="WorkflowDefinition with this name already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.get("/workflow-definitions/", response_model=List[WorkflowDefinitionRead])
def list_workflow_definitions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    defs = db.query(WorkflowDefinition).offset(skip).limit(limit).all()
    return [WorkflowDefinitionRead.model_validate(d) for d in defs]

@router.get("/workflow-definitions/{definition_id}", response_model=WorkflowDefinitionRead)
def get_workflow_definition(definition_id: uuid.UUID, db: Session = Depends(get_db)):
    wf_def = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
    if not wf_def:
        raise HTTPException(status_code=404, detail="WorkflowDefinition not found")
    return WorkflowDefinitionRead.model_validate(wf_def)

@router.put("/workflow-definitions/{definition_id}", response_model=WorkflowDefinitionRead)
def update_workflow_definition(definition_id: uuid.UUID, wf_def_update: WorkflowDefinitionCreate = Body(...), db: Session = Depends(get_db)):
    wf_def = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
    if not wf_def:
        raise HTTPException(status_code=404, detail="WorkflowDefinition not found")
    wf_def.name = wf_def_update.name
    wf_def.description = wf_def_update.description
    wf_def.graph_representation = wf_def_update.definition_dsl or {}
    try:
        db.commit()
        db.refresh(wf_def)
        return WorkflowDefinitionRead.model_validate(wf_def)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="WorkflowDefinition with this name already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.delete("/workflow-definitions/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_definition(definition_id: uuid.UUID, db: Session = Depends(get_db)):
    wf_def = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
    if not wf_def:
        raise HTTPException(status_code=404, detail="WorkflowDefinition not found")
    db.delete(wf_def)
    db.commit()
    return

# --- WorkflowRun CRUD ---

@router.post("/workflow-definitions/{definition_id}/runs/", response_model=WorkflowRunRead, status_code=status.HTTP_201_CREATED)
def create_workflow_run(definition_id: uuid.UUID, run_create: WorkflowRunCreate = Body(...), db: Session = Depends(get_db)):
    wf_def = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
    if not wf_def:
        raise HTTPException(status_code=404, detail="WorkflowDefinition not found")
    run = WorkflowRun(
        workflow_definition_id=definition_id,
        status="PENDING",
        run_parameters=run_create.run_parameters or {},
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return WorkflowRunRead.model_validate(run)

@router.get("/workflow-definitions/{definition_id}/runs/", response_model=List[WorkflowRunRead])
def list_workflow_runs(definition_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = db.query(WorkflowRun).filter(WorkflowRun.workflow_definition_id == definition_id).offset(skip).limit(limit).all()
    return [WorkflowRunRead.model_validate(r) for r in runs]

@router.get("/workflow-runs/{run_id}", response_model=WorkflowRunRead)
def get_workflow_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="WorkflowRun not found")
    return WorkflowRunRead.model_validate(run)

@router.delete("/workflow-runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="WorkflowRun not found")
    db.delete(run)
    db.commit()
    return
