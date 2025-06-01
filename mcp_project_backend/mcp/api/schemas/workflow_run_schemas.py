"""
Pydantic schemas for Workflow Runs and related execution data.

These models are used for API requests and responses related to workflow execution in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkflowRunStatusEnum(str, Enum):
    """
    Enum representing the status of a workflow run.
    Matches frontend types and database values.
    """
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"
    ABORTED = "Aborted"

class WorkflowRunStepLogSchema(BaseModel):
    """
    Schema for a log or event within a workflow run step.

    Attributes:
        id (int): Unique identifier for the log/event.
        timestamp (datetime): Timestamp of the log/event.
        step_name (str): Name or ID of the step.
        event_type (str): Type of event (e.g., "LOG", "STATUS_UPDATE", "ERROR", "ARTIFACT_PRODUCED").
        message (Optional[str]): Optional message for the event.
        payload (Optional[Dict[str, Any]]): Optional payload with additional event data.
    """
    id: int = Field(..., description="Unique identifier for the log/event.")
    timestamp: datetime = Field(..., description="Timestamp of the log/event.")
    step_name: str = Field(..., description="Name or ID of the workflow step.")
    event_type: str = Field(..., description="Type of event (e.g., LOG, STATUS_UPDATE, ERROR, ARTIFACT_PRODUCED).")
    message: Optional[str] = Field(None, description="Optional message for the event.")
    payload: Optional[Dict[str, Any]] = Field(None, description="Optional payload with additional event data.")

    class Config:
        orm_mode = True

class WorkflowRunBase(BaseModel):
    """
    Base schema for a workflow run.

    Attributes:
        workflow_definition_id (int): ID of the workflow definition being executed.
        status (WorkflowRunStatusEnum): Status of the workflow run.
        runtime_inputs (Optional[Dict[str, Any]]): Inputs provided at runtime, if not all defined in WorkflowDefinition.
    """
    workflow_definition_id: int = Field(..., description="ID of the workflow definition being executed.")
    status: WorkflowRunStatusEnum = Field(default=WorkflowRunStatusEnum.PENDING, description="Status of the workflow run.")
    runtime_inputs: Optional[Dict[str, Any]] = Field(None, description="Inputs provided at runtime.")

class WorkflowRunCreateRequest(BaseModel):
    """
    Schema for creating a workflow run (POST /workflows/{id}/execute).
    Allows specifying runtime parameters to override or provide at execution time.
    """
    runtime_parameters: Optional[Dict[str, Any]] = Field(None, description="Runtime parameters for workflow execution.")

class WorkflowRunRead(WorkflowRunBase):
    """
    Schema for reading a workflow run from the database/API.
    Includes run ID, timestamps, duration, outputs, and (optionally) logs/events.
    """
    id: int = Field(..., description="Unique identifier for the workflow run.")
    created_at: datetime = Field(..., description="Timestamp when the run was created.")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the run started.")
    ended_at: Optional[datetime] = Field(None, description="Timestamp when the run ended.")
    duration_seconds: Optional[float] = Field(None, description="Duration of the run in seconds.")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Final outputs of the workflow run.")
    # logs_or_events: List[WorkflowRunStepLogSchema] = Field(default_factory=list, description="Detailed step events.")

    class Config:
        orm_mode = True
