from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from mcp.api.deps import get_db, get_current_user
from mcp.core.services.api_key_service import APIKeyService
from mcp.schemas.api_key import APIKeyCreate, APIKeyRead, APIKeyResponse

router = APIRouter()

@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new API key."""
    service = APIKeyService(db)
    api_key = service.create_api_key(
        name=data.name,
        created_by=current_user,
        owner_id=data.owner_id,
        owner_type=data.owner_type,
        expires_in_days=data.expires_in_days
    )
    
    # Include the raw key in the response
    response = APIKeyResponse.from_orm(api_key)
    response.key = api_key.raw_key
    return response

@router.get("/", response_model=List[APIKeyRead])
async def list_api_keys(
    owner_id: str = None,
    owner_type: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """List API keys with optional filtering."""
    service = APIKeyService(db)
    return service.list_api_keys(
        owner_id=owner_id,
        owner_type=owner_type,
        active_only=active_only
    )

@router.get("/{key_id}", response_model=APIKeyRead)
async def get_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get an API key by ID."""
    service = APIKeyService(db)
    api_key = service.get_api_key(key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return api_key

@router.delete("/{key_id}", response_model=APIKeyRead)
async def deactivate_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Deactivate an API key."""
    service = APIKeyService(db)
    return service.deactivate_api_key(key_id) 