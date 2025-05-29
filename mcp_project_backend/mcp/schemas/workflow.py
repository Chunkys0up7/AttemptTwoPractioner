"""
Pydantic schemas for WorkflowDefinition and WorkflowRun API operations.
"""
import uuid
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from mcp.db.models.workflow import WorkflowRunStatus  # Import the enum

# --- WorkflowRun Schemas ---


class WorkflowRunBase(BaseModel):
    """Base schema for WorkflowRun."""
    workflow_definition_id: uuid.UUID
    status: WorkflowRunStatus = Field(default=WorkflowRunStatus.PENDING)
    run_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    results: Optional[Dict[str, Any]] = Field(default=None)


class WorkflowRunCreate(BaseModel):
    """Schema for creating a WorkflowRun (typically via POST /run endpoint). Body of the request."""
    run_parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Parameters for this specific workflow run.")
    # workflow_definition_id is a path parameter in the endpoint


class WorkflowRunRead(WorkflowRunBase):
    """Schema for reading/returning a WorkflowRun."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True  # Ensure enum values are used in serialization

# --- WorkflowDefinition Schemas (Basic Placeholders) ---
# These will be expanded significantly later.


class WorkflowDefinitionBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    # Definition structure (e.g., list of steps, graph) will go here - complex field
    definition_dsl: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="DSL representing the workflow structure")


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    pass


class WorkflowDefinitionRead(WorkflowDefinitionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # Potentially include associated runs or other relevant info
    # runs: List[WorkflowRunRead] = []

    class Config:
        from_attributes = True
