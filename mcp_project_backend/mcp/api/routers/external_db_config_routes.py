"""
API Endpoints for External Database Configuration CRUD operations.
"""
import uuid
# from typing import Optional, Any # Unused

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError # Unused

from mcp.db.session import get_db
from mcp.schemas.external_db_config import (
    ExternalDbConfigCreate, ExternalDbConfigRead, ExternalDbConfigUpdate, ExternalDbConfigList
)
from mcp.core.services.external_db_config_service import ExternalDbConfigService

router = APIRouter(
    prefix="/external-db-configs",
    tags=["External Database Configurations"],
)

# Dependency to get ExternalDbConfigService instance


def get_ext_db_config_service(db: Session = Depends(get_db)) -> ExternalDbConfigService:
    return ExternalDbConfigService(db)


@router.post("/", response_model=ExternalDbConfigRead, status_code=status.HTTP_201_CREATED)
def create_external_db_config(
    config_create: ExternalDbConfigCreate,
    service: ExternalDbConfigService = Depends(get_ext_db_config_service)
):
    """Create a new External Database Configuration."""
    try:
        return service.create_config(config_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as _e:
        # Log _e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating external DB config.")


@router.get("/", response_model=ExternalDbConfigList)
def list_external_db_configs(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200,
                       description="Maximum number of items to return"),
    service: ExternalDbConfigService = Depends(get_ext_db_config_service)
):
    """List External Database Configurations."""
    configs, total = service.list_configs(skip=skip, limit=limit)
    return {"items": configs, "total": total}


@router.get("/{config_id}", response_model=ExternalDbConfigRead)
def get_external_db_config(
    config_id: uuid.UUID,
    service: ExternalDbConfigService = Depends(get_ext_db_config_service)
):
    """Get a specific External Database Configuration by its ID."""
    db_config = service.get_config(config_id)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="External DB Config not found")
    return db_config


@router.put("/{config_id}", response_model=ExternalDbConfigRead)
def update_external_db_config(
    config_id: uuid.UUID,
    config_update: ExternalDbConfigUpdate,
    service: ExternalDbConfigService = Depends(get_ext_db_config_service)
):
    """Update an External Database Configuration."""
    try:
        updated_config = service.update_config(config_id, config_update)
        if updated_config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="External DB Config not found")
        return updated_config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as _e:
        # Log _e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error updating external DB config.")


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_external_db_config(
    config_id: uuid.UUID,
    service: ExternalDbConfigService = Depends(get_ext_db_config_service)
):
    """Delete an External Database Configuration."""
    if not service.delete_config(config_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="External DB Config not found")
    return
