"""
Pydantic schemas for generic entity detail responses and action log summaries.

These models are used for API responses when fetching details of various entity types in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class EntityActionLogSummary(BaseModel):
    """
    Summary of an action related to an entity (for audit/history purposes).

    Attributes:
        timestamp (str): Timestamp of the action (ISO 8601 string).
        action_type (str): Type of action performed (e.g., 'CREATE', 'UPDATE', 'DELETE').
        actor_id (Optional[str]): ID of the actor who performed the action.
    """
    timestamp: str = Field(..., description="Timestamp of the action (ISO 8601 string).")
    action_type: str = Field(..., description="Type of action performed (e.g., 'CREATE', 'UPDATE', 'DELETE').")
    actor_id: Optional[str] = Field(None, description="ID of the actor who performed the action.")

class EntityDetailResponse(BaseModel):
    """
    Generic response model for fetching details of any entity type.

    Attributes:
        entity_type (str): Type of the entity (e.g., 'MCPVersion', 'WorkflowRun').
        entity_id (str): Unique identifier for the entity (could be int, str, or UUID as string).
        data (Dict[str, Any]): The actual entity data (e.g., serialized MCPVersionRead or WorkflowRunRead).
        related_actions (Optional[List[EntityActionLogSummary]]): List of related action log summaries.
    """
    entity_type: str = Field(..., description="Type of the entity (e.g., 'MCPVersion', 'WorkflowRun').")
    entity_id: str = Field(..., description="Unique identifier for the entity (could be int, str, or UUID as string).")
    data: Dict[str, Any] = Field(..., description="The actual entity data (e.g., serialized MCPVersionRead or WorkflowRunRead).")
    related_actions: Optional[List[EntityActionLogSummary]] = Field(default_factory=list, description="List of related action log summaries.")
