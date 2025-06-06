from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class TemplateBase(BaseModel):
    """Base schema for template data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_public: bool = Field(default=False)

class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    content: Dict[str, Any] = Field(..., description="Template content in JSON format")

class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    content: Optional[Dict[str, Any]] = Field(None, description="Updated template content")
    changes: Optional[str] = Field(None, max_length=1000, description="Description of changes made")

class TemplateVersionCreate(BaseModel):
    """Schema for creating a new template version."""
    content: Dict[str, Any] = Field(..., description="Template content in JSON format")
    changes: str = Field(..., max_length=1000, description="Description of changes made")

class TemplateVersionResponse(BaseModel):
    """Schema for template version response."""
    id: int
    template_id: int
    version: int
    content: Dict[str, Any]
    changes: str
    created_by: int
    created_at: datetime

    class Config:
        orm_mode = True

class TemplateResponse(TemplateBase):
    """Schema for template response."""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    current_version: int

    class Config:
        orm_mode = True

class TemplateStats(BaseModel):
    """Schema for template statistics."""
    total_templates: int
    public_templates: int
    categories: int 