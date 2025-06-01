"""
API Endpoints for managing Workflow Definitions and their Workflow Steps.

This router provides CRUD operations for WorkflowDefinitions and for managing WorkflowSteps within a workflow (adding, removing, reordering MCP versions as steps).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from mcp.db.session import get_db
from mcp.core.config import settings
from mcp.api.schemas.workflow_definition_schemas import (
    WorkflowDefinitionCreate, WorkflowDefinitionRead, WorkflowDefinitionUpdate,
    WorkflowStepCreate, WorkflowStepRead
)
from mcp.db.crud.crud_workflow_definition import crud_workflow_definition, crud_workflow_step

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/workflow-definitions",
    tags=["Workflow Definitions"],
)

@router.post("/", response_model=WorkflowDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_workflow_definition(
    wf_def_in: WorkflowDefinitionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new Workflow Definition, optionally with steps.
    """
    try:
        wf_def = crud_workflow_definition.create_with_steps(db=db, obj_in=wf_def_in)
        return wf_def
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating workflow definition: {e}")

@router.get("/", response_model=List[WorkflowDefinitionRead])
def list_workflow_definitions(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List all Workflow Definitions (paginated).
    """
    defs = crud_workflow_definition.get_multi(db, skip=skip, limit=limit)
    return defs

@router.get("/{wf_def_id}", response_model=WorkflowDefinitionRead)
def get_workflow_definition(
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    db: Session = Depends(get_db)
):
    """
    Get a Workflow Definition by ID, including its steps.
    """
    wf_def = crud_workflow_definition.get_with_steps(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return wf_def

@router.put("/{wf_def_id}", response_model=WorkflowDefinitionRead)
def update_workflow_definition(
    wf_def_id: int,
    wf_def_update: WorkflowDefinitionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a Workflow Definition's metadata (not steps).
    """
    db_obj = crud_workflow_definition.get(db, id=wf_def_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    updated = crud_workflow_definition.update(db, db_obj=db_obj, obj_in=wf_def_update)
    return updated

@router.delete("/{wf_def_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_definition(
    wf_def_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a Workflow Definition and all its steps.
    """
    obj = crud_workflow_definition.remove(db, id=wf_def_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return

# --- Workflow Step Endpoints ---

@router.post("/{wf_def_id}/steps/", response_model=WorkflowStepRead, status_code=status.HTTP_201_CREATED)
def add_workflow_step(
    wf_def_id: int,
    step_in: WorkflowStepCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new step to a Workflow Definition.
    """
    # Ensure parent exists
    wf_def = crud_workflow_definition.get(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    step = crud_workflow_step.create(db, obj_in={**step_in.model_dump(), "workflow_definition_id": wf_def_id})
    return step

@router.delete("/{wf_def_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_step(
    wf_def_id: int,
    step_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a step from a Workflow Definition.
    """
    step = crud_workflow_step.get(db, id=step_id)
    if not step or step.workflow_definition_id != wf_def_id:
        raise HTTPException(status_code=404, detail="Workflow Step not found for this Workflow Definition")
    crud_workflow_step.remove(db, id=step_id)
    return

@router.put("/{wf_def_id}/steps/{step_id}", response_model=WorkflowStepRead)
def update_workflow_step(
    wf_def_id: int,
    step_id: int,
    step_update: WorkflowStepCreate,
    db: Session = Depends(get_db)
):
    """
    Update a step in a Workflow Definition.
    """
    step = crud_workflow_step.get(db, id=step_id)
    if not step or step.workflow_definition_id != wf_def_id:
        raise HTTPException(status_code=404, detail="Workflow Step not found for this Workflow Definition")
    updated = crud_workflow_step.update(db, db_obj=step, obj_in=step_update)
    return updated

@router.get("/{wf_def_id}/steps/", response_model=List[WorkflowStepRead])
def list_workflow_steps(
    wf_def_id: int,
    db: Session = Depends(get_db)
):
    """
    List all steps for a Workflow Definition.
    """
    wf_def = crud_workflow_definition.get_with_steps(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return wf_def.steps
