from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...core.security import get_current_user
from ...schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateVersionResponse,
    TemplateStats
)
from ...api.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=TemplateResponse)
def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new workflow template."""
    service = TemplateService(db)
    template = service.create_template(template_data, current_user["id"])
    return template

@router.get("/", response_model=List[TemplateResponse])
def list_templates(
    category: Optional[str] = None,
    search: Optional[str] = None,
    public_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List templates with optional filtering."""
    service = TemplateService(db)
    templates = service.list_templates(
        current_user["id"],
        category=category,
        search=search,
        public_only=public_only
    )
    return templates

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific template."""
    service = TemplateService(db)
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_public and template.created_by != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this template")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a template."""
    service = TemplateService(db)
    template = service.update_template(template_id, template_data, current_user["id"])
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a template."""
    service = TemplateService(db)
    if not service.delete_template(template_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

@router.get("/{template_id}/versions", response_model=List[TemplateVersionResponse])
def list_template_versions(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all versions of a template."""
    service = TemplateService(db)
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_public and template.created_by != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this template")
    return service.list_template_versions(template_id)

@router.get("/{template_id}/versions/{version}", response_model=TemplateVersionResponse)
def get_template_version(
    template_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific version of a template."""
    service = TemplateService(db)
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_public and template.created_by != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this template")
    
    template_version = service.get_template_version(template_id, version)
    if not template_version:
        raise HTTPException(status_code=404, detail="Template version not found")
    return template_version

@router.get("/search", response_model=List[TemplateResponse])
def search_templates(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    public_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search templates by name or description."""
    service = TemplateService(db)
    templates = service.list_templates(
        current_user["id"],
        category=category,
        search=q,
        public_only=public_only
    )
    return templates

@router.get("/categories", response_model=List[str])
def get_template_categories():
    """
    Get a list of available template categories (stub/in-memory).
    """
    return [
        "Data Processing",
        "Machine Learning",
        "ETL",
        "Visualization",
        "Reporting",
        "Automation",
        "Custom"
    ]

@router.get("/stats", response_model=TemplateStats)
def get_template_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get template statistics."""
    service = TemplateService(db)
    return service.get_template_stats(current_user["id"]) 