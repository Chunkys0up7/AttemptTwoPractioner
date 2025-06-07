"""
Pydantic schemas for Workflow Definitions and Workflow Steps with enhanced validation and monitoring.
These models are used for API requests and responses related to workflow definitions in the MCP backend.
Includes comprehensive validation and error handling.
"""

from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, List, Dict, Any, TypeVar, Generic, Type
import uuid
from datetime import datetime
import logging

from mcp.core.exceptions import WorkflowDefinitionError
from mcp.monitoring.performance import performance_monitor

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class WorkflowStepBase(BaseModel):
    """
    Base schema for a workflow step within a workflow definition.

    Attributes:
        name: Name of the step
        mcp_version_id: ID of the MCPVersion to use
        mcp_type: Type of the MCP component
        description: Optional description
        input_mappings: Input mappings for the step
        order: Execution order
        tags: Optional tags
    """
    name: str = Field(..., description="Name of the workflow step", min_length=1, max_length=255)
    mcp_version_id: uuid.UUID = Field(..., description="ID of the MCPVersion to use")
    mcp_type: str = Field(..., description="Type of the MCP component", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="Optional description", max_length=1000)
    input_mappings: Dict[str, Any] = Field(default_factory=dict, description="Input mappings for this step")
    order: int = Field(..., description="Execution order", ge=0)
    tags: List[str] = Field(default_factory=list, description="Optional tags", max_items=20)

    @validator('name')
    def validate_name(cls, v):
        """Validate step name format."""
        if not v.strip():
            raise ValueError("Step name cannot be empty")
        return v.strip()

    @validator('input_mappings')
    def validate_input_mappings(cls, v):
        """Validate input mappings structure."""
        if not isinstance(v, dict):
            raise ValueError("Input mappings must be a dictionary")
        for key, mapping in v.items():
            if not isinstance(mapping, dict):
                raise ValueError(f"Mapping for {key} must be a dictionary")
            if 'source_step_id' in mapping and not isinstance(mapping['source_step_id'], str):
                raise ValueError(f"source_step_id for {key} must be a string")
        return v

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        if any(len(tag) > 50 for tag in v):
            raise ValueError("Tags cannot exceed 50 characters")
        return v

class WorkflowStepCreate(WorkflowStepBase):
    """
    Schema for creating a workflow step.
    Inherits all fields from WorkflowStepBase with enhanced validation.
    """
    @validator('mcp_version_id')
    def validate_mcp_version_id(cls, v):
        """Validate MCP version ID format."""
        try:
            uuid.UUID(str(v))
            return v
        except ValueError:
            raise ValueError("Invalid MCP version ID format")

class WorkflowStepRead(WorkflowStepBase):
    """
    Schema for reading a workflow step from the database/API.
    Includes the step's ID and the parent workflow definition ID.
    """
    id: uuid.UUID = Field(..., description="Unique identifier for the step")
    workflow_definition_id: uuid.UUID = Field(..., description="ID of the parent workflow definition")
    created_at: datetime = Field(..., description="When the step was created")
    updated_at: datetime = Field(..., description="When the step was last updated")

    @validator('id', 'workflow_definition_id')
    def validate_uuid(cls, v):
        """Validate UUID format."""
        try:
            uuid.UUID(str(v))
            return v
        except ValueError:
            raise ValueError("Invalid UUID format")

class WorkflowDefinitionBase(BaseModel):
    """
    Base schema for workflow definitions.

    Attributes:
        name: Name of the workflow
        description: Optional description
        graph_representation: Workflow graph structure
        version: Version number
        is_active: Active status flag
        tags: Optional tags
    """
    name: str = Field(..., description="Name of the workflow", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Optional description", max_length=1000)
    graph_representation: Dict[str, Any] = Field(..., description="Workflow graph structure")
    version: str = Field("1.0.0", description="Version number", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    is_active: bool = Field(True, description="Active status")
    tags: List[str] = Field(default_factory=list, description="Optional tags", max_items=20)

    @validator('name')
    def validate_name(cls, v):
        """Validate workflow name format."""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty")
        return v.strip()

    @validator('graph_representation')
    def validate_graph(cls, v):
        """Validate workflow graph structure."""
        try:
            if not isinstance(v, dict):
                raise ValueError("Graph must be a dictionary")
            if 'nodes' not in v or 'edges' not in v:
                raise ValueError("Graph must contain nodes and edges")
            return v
        except Exception as e:
            logger.error(f"Invalid workflow graph: {e}")
            performance_monitor.increment_error("workflow_graph_validation", str(e))
            raise WorkflowDefinitionError(f"Invalid workflow graph: {str(e)}")

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        if any(len(tag) > 50 for tag in v):
            raise ValueError("Tags cannot exceed 50 characters")
        return v

class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    """
    Schema for creating a workflow definition.
    Inherits all fields from WorkflowDefinitionBase with enhanced validation.
    """
    steps: List[WorkflowStepCreate] = Field(default_factory=list, description="List of workflow steps")

    @validator('steps')
    def validate_steps(cls, v):
        """Validate workflow steps."""
        if not isinstance(v, list):
            raise ValueError("Steps must be a list")
        if len(v) > 100:
            raise ValueError("Maximum 100 steps allowed")
        return v

class WorkflowDefinitionRead(WorkflowDefinitionBase):
    """
    Schema for reading a workflow definition from the database/API.
    Includes additional metadata fields.
    """
    id: uuid.UUID = Field(..., description="Unique identifier for the workflow")
    created_at: datetime = Field(..., description="When the workflow was created")
    updated_at: datetime = Field(..., description="When the workflow was last updated")
    created_by: str = Field(..., description="User who created the workflow")
    updated_by: str = Field(..., description="User who last updated the workflow")
    steps: List[WorkflowStepRead] = Field(default_factory=list, description="List of workflow steps")

    @validator('id')
    def validate_uuid(cls, v):
        """Validate UUID format."""
        try:
            uuid.UUID(str(v))
            return v
        except ValueError:
            raise ValueError("Invalid UUID format")
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
