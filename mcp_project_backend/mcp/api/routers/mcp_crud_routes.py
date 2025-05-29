"""
API Endpoints for MCP Definition and Version CRUD operations.
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from mcp.db.session import get_db
from mcp.core.config import settings
from mcp.schemas.mcp import (
    MCPDefinitionCreate, MCPDefinitionRead, MCPDefinitionUpdate, MCPDefinitionList,
    MCPVersionCreate, MCPVersionRead, MCPVersionUpdate
)
from mcp.core.services.mcp_service import MCPService

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/mcp-definitions",
    tags=["MCP Definitions & Versions"],
)

# Placeholder for actor_id until authentication is implemented
# In a real application, this would come from an auth dependency (e.g., get_current_user.id)
DUMMY_ACTOR_ID = "system_actor_placeholder_uuid"

# Dependency to get MCPService instance


def get_mcp_service(db: Session = Depends(get_db)) -> MCPService:
    return MCPService(db)

# --- MCPDefinition Endpoints ---


@router.post("/", response_model=MCPDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_mcp_definition(
    mcp_def_create: MCPDefinitionCreate,
    db: Session = Depends(get_db)
) -> MCPDefinitionRead:
    """
    Create a new MCP Definition. Optionally, an initial version can be created with it.
    """
    service = MCPService(db)
    try:
        db_mcp_def = service.create_mcp_definition(
            mcp_def_create=mcp_def_create, actor_id=DUMMY_ACTOR_ID)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # Catch specific HTTP exceptions from service (e.g., for External DB config not found)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        # Log the exception for debugging
        # Replace with proper logging
        print(f"Error creating MCP Definition: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error during MCP Definition creation.")
    return MCPDefinitionRead.model_validate(db_mcp_def)


@router.get("/definitions/", response_model=MCPDefinitionList)
def list_mcp_definitions(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200,
                       description="Maximum number of items to return"),
    service: MCPService = Depends(get_mcp_service)
):
    """List MCP Definitions with pagination."""
    definitions, total = service.list_mcp_definitions(skip=skip, limit=limit)
    return {"items": definitions, "total": total}


@router.get("/definitions/{mcp_def_id}", response_model=MCPDefinitionRead)
def get_mcp_definition(
    mcp_def_id: uuid.UUID,
    service: MCPService = Depends(get_mcp_service)
):
    """Get a specific MCP Definition by its ID, including its versions."""
    db_mcp_def = service.get_mcp_definition(mcp_def_id)
    if db_mcp_def is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="MCPDefinition not found")
    return db_mcp_def


@router.put("/{definition_id}", response_model=MCPDefinitionRead)
async def update_mcp_definition(
    definition_id: uuid.UUID,
    mcp_def_update: MCPDefinitionUpdate,
    db: Session = Depends(get_db)
) -> MCPDefinitionRead:
    """
    Update an existing MCP Definition's properties (name, description).
    """
    service = MCPService(db)
    try:
        updated_def = service.update_mcp_definition(
            mcp_def_id=definition_id, mcp_def_update=mcp_def_update, actor_id=DUMMY_ACTOR_ID)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception
        print(f"Error updating MCP Definition {definition_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error during MCP Definition update.")
    if updated_def is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="MCPDefinition not found")
    return MCPDefinitionRead.model_validate(updated_def)


@router.delete("/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_definition(
    definition_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an MCP Definition and all its associated versions.
    """
    service = MCPService(db)
    try:
        deleted = service.delete_mcp_definition(
            mcp_def_id=definition_id, actor_id=DUMMY_ACTOR_ID)
    except Exception as e:
        # Log the exception
        print(f"Error deleting MCP Definition {definition_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error during MCP Definition deletion.")

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="MCPDefinition not found")
    return

# --- MCPVersion Endpoints (nested under definitions) ---


@router.post("/{definition_id}/versions/", response_model=MCPVersionRead, status_code=status.HTTP_201_CREATED)
async def create_mcp_version_for_definition(
    definition_id: uuid.UUID,
    version_create: MCPVersionCreate,
    db: Session = Depends(get_db)
) -> MCPVersionRead:
    """
    Create a new version for a specific MCP Definition.
    """
    service = MCPService(db)
    try:
        db_mcp_version = service.create_mcp_version(
            definition_id=definition_id, version_create=version_create, actor_id=DUMMY_ACTOR_ID)
    # Catch HTTP exceptions from service (e.g. 404 for definition or external db config)
    except HTTPException as http_exc:
        raise http_exc
    # Catch other value errors (e.g., config type mismatch)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception
        print(
            f"Error creating MCP Version for definition {definition_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error during MCP Version creation.")

    if db_mcp_version is None:  # Should be caught by service raising HTTPException for not found definition
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="MCPDefinition not found to create version for.")
    return MCPVersionRead.model_validate(db_mcp_version)


@router.get("/definitions/{mcp_def_id}/versions/", response_model=List[MCPVersionRead])
def list_mcp_versions_for_definition(
    mcp_def_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200,
                       description="Maximum number of items to return"),
    service: MCPService = Depends(get_mcp_service)
):
    """List all MCP Versions for a given MCP Definition."""
    db_mcp_def = service.get_mcp_definition(mcp_def_id)
    if not db_mcp_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="MCPDefinition not found")
    versions, total = service.list_mcp_versions_for_definition(
        mcp_def_id, skip=skip, limit=limit)
    return {"items": versions, "total": total}


# Independent endpoint to get any version by its ID
@router.get("/versions/{mcp_version_id}", response_model=MCPVersionRead)
def get_mcp_version(
    mcp_version_id: uuid.UUID,
    service: MCPService = Depends(get_mcp_service)
):
    """Get a specific MCP Version by its unique ID."""
    db_mcp_ver = service.get_mcp_version(mcp_version_id)
    if db_mcp_ver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="MCPVersion not found")
    return db_mcp_ver


@router.put("/{definition_id}/versions/{version_id}", response_model=MCPVersionRead)
async def update_mcp_version(
    # Path param for consistency, though version_id is primary key
    definition_id: uuid.UUID,
    version_id: uuid.UUID,
    version_update: MCPVersionUpdate,
    db: Session = Depends(get_db)
) -> MCPVersionRead:
    """
    Update an existing MCP Version.
    Note: `definition_id` in path is for route structure, `version_id` is the key for update.
    The service layer should ensure the version belongs to the definition if such check is needed,
    though typically `version_id` is globally unique.
    """
    service = MCPService(db)
    try:
        updated_version = service.update_mcp_version(
            version_id=version_id, version_update=version_update, actor_id=DUMMY_ACTOR_ID)
    except HTTPException as http_exc:  # Catch HTTP exceptions from service
        raise http_exc
    except ValueError as e:  # Catch value errors from service
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception
        print(f"Error updating MCP Version {version_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error during MCP Version update.")

    if updated_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="MCPVersion not found")

    # Optional: Verify version belongs to definition_id if strict hierarchy is enforced at API level
    if updated_version.mcp_definition_id != definition_id:
        # This case might indicate a logic error or a need for more specific error handling
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Version {version_id} does not belong to definition {definition_id}. Update not allowed through this path.")

    return MCPVersionRead.model_validate(updated_version)


@router.delete("/{definition_id}/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_version(
    definition_id: uuid.UUID,  # Path param for consistency
    version_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an MCP Version.
    """
    service = MCPService(db)
    # ... (existing check for version belonging to definition can be added here or in service)
    # For now, service.delete_mcp_version only needs version_id
    try:
        # Optional: First, verify the version belongs to the definition_id if strict route integrity is needed
        # version_to_delete = service.get_mcp_version(version_id)
        # if not version_to_delete or version_to_delete.mcp_definition_id != definition_id:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        #                         detail=f"MCPVersion {version_id} not found under definition {definition_id}.")

        deleted = service.delete_mcp_version(
            version_id=version_id, actor_id=DUMMY_ACTOR_ID)
    except Exception as e:
        # Log the exception
        print(f"Error deleting MCP Version {version_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error during MCP Version deletion.")

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="MCPVersion not found or already deleted")
    return
