from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class APIKeyBase(BaseModel):
    """Base schema for API key data."""
    name: str = Field(..., description="A descriptive name for the API key")
    owner_id: Optional[str] = Field(None, description="Optional ID of the key owner")
    owner_type: Optional[str] = Field(None, description="Optional type of the key owner")
    expires_in_days: Optional[int] = Field(None, description="Optional number of days until the key expires")

class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key."""
    pass

class APIKeyRead(APIKeyBase):
    """Schema for reading API key data."""
    id: int
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    created_by: str
    
    class Config:
        from_attributes = True

class APIKeyResponse(APIKeyRead):
    """Schema for API key response, including the raw key on creation."""
    key: Optional[str] = Field(None, description="The raw API key (only available immediately after creation)")
    
    class Config:
        from_attributes = True 