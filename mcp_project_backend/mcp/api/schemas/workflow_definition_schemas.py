"""
Pydantic schemas for Workflow Definitions and Workflow Steps.

These models are used for API requests and responses related to workflow definitions in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class WorkflowStepBase(BaseModel):
    """
    Base schema for a workflow step within a workflow definition.

    Attributes:
        name (str): Name of the step.
        mcp_version_id (int): ID of the specific MCPVersion to use for this step.
        mcp_type (SpecificComponentType): Type of the MCP component used in this step.
        description (Optional[str]): Optional description of the step.
        input_mappings (Optional[Dict[str, Any]]):
            How inputs are mapped to this step's MCP. Example:
            {
                "mcp_input_param_name": {
                    "source_step_id": "step_A_id",
                    "source_output_name": "output_X"
                },
                "another_param": {"static_value": "some value"}
            }
        order (int): Execution order of the step within the workflow.
        tags (Optional[List[str]]): Optional tags for categorizing the step.
    """
    name: str = Field(..., description="Name of the workflow step.")
    mcp_version_id: int = Field(..., description="ID of the MCPVersion to use for this step.")
    mcp_type: SpecificComponentType = Field(..., description="Type of the MCP component used in this step.")
    description: Optional[str] = Field(None, description="Optional description of the step.")
    input_mappings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input mappings for this step.")
    order: int = Field(..., description="Execution order of the step within the workflow.")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional tags for categorizing the step.")

class WorkflowStepCreate(WorkflowStepBase):
    """
    Schema for creating a workflow step.
    Inherits all fields from WorkflowStepBase.
    """
    pass

class WorkflowStepRead(WorkflowStepBase):
    """
    Schema for reading a workflow step from the database/API.
    Includes the step's ID and the parent workflow definition ID.
    """
    id: int = Field(..., description="Unique identifier for the workflow step.")
    workflow_definition_id: int = Field(..., description="ID of the parent workflow definition.")

    class Config:
        orm_mode = True

class WorkflowDefinitionBase(BaseModel):
    """
    Base schema for a workflow definition.

    Attributes:
        name (str): Name of the workflow definition.
        description (Optional[str]): Optional description of the workflow.
        tags (Optional[List[str]]): List of tags for categorization.
    """
    name: str = Field(..., description="Name of the workflow definition.")
    description: Optional[str] = Field(None, description="Optional description of the workflow.")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for the workflow definition.")

class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    """
    Schema for creating a workflow definition, including its steps.
    """
    steps: Optional[List[WorkflowStepCreate]] = Field(default_factory=list, description="List of steps in the workflow.")

class WorkflowDefinitionUpdate(WorkflowDefinitionBase):
    """
    Schema for updating a workflow definition.
    The 'name' field is optional for updates.
    Updating steps is often handled by dedicated endpoints or by re-creation.
    """
    name: Optional[str] = Field(None, description="Updated name of the workflow definition.")
    # steps: Optional[List[WorkflowStepCreate]] = Field(default_factory=list, description="Updated steps (if supported).")

class WorkflowDefinitionRead(WorkflowDefinitionBase):
    """
    Schema for reading a workflow definition from the database/API.
    Includes the workflow's ID, steps, and optional owner ID.
    """
    id: int = Field(..., description="Unique identifier for the workflow definition.")
    steps: List[WorkflowStepRead] = Field(default_factory=list, description="List of steps in the workflow.")
    owner_id: Optional[int] = Field(None, description="ID of the workflow owner, if applicable.")

    class Config:
        orm_mode = True
