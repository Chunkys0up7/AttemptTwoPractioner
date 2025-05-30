from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from mcp.db.session import SessionLocal
from mcp.core.services.api_key_service import APIKeyService

# API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_db() -> Generator:
    """Get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(request: Request) -> str:
    """Get the current user ID from the request context."""
    # In a real implementation, this would extract the user ID from the auth token
    return request.headers.get("X-User-ID", "system")

async def get_api_key_user(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> str:
    """Validate API key and return the associated user ID."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
    
    service = APIKeyService(db)
    api_key_obj = service.validate_api_key(api_key)
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    return api_key_obj.owner_id or "system"
