"""
Pydantic schemas for dashboard-specific API endpoints.

These models are used for API requests and responses related to dashboard data in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class DashboardSummaryItem(BaseModel):
    """
    Represents a summary item for the dashboard (e.g., recent components, trending workflows).

    Attributes:
        name (str): Name of the item (e.g., workflow/component name).
        count (int): Count or metric associated with the item.
        link (Optional[str]): Optional link to the item's detail page.
    """
    name: str = Field(..., description="Name of the item (e.g., workflow/component name).")
    count: int = Field(..., description="Count or metric associated with the item.")
    link: Optional[str] = Field(None, description="Optional link to the item's detail page.")

class DashboardSystemHealth(BaseModel):
    """
    Represents the health status of a system service for the dashboard.

    Attributes:
        service_name (str): Name of the service (e.g., 'Database', 'Redis').
        status (str): Health status (e.g., 'OK', 'Warning', 'Error').
        details (Optional[str]): Optional details about the health status.
    """
    service_name: str = Field(..., description="Name of the service (e.g., 'Database', 'Redis').")
    status: str = Field(..., description="Health status (e.g., 'OK', 'Warning', 'Error').")
    details: Optional[str] = Field(None, description="Optional details about the health status.")

class DashboardSummary(BaseModel):
    """
    Represents the overall dashboard summary returned by the API.

    Attributes:
        active_workflow_runs (int): Number of currently active workflow runs.
        completed_runs_today (int): Number of completed runs today.
        failed_runs_today (int): Number of failed runs today.
        total_mcp_definitions (int): Total number of MCP definitions.
        total_workflow_definitions (int): Total number of workflow definitions.
        recent_components (List[DashboardSummaryItem]): List of recent components.
        trending_workflows (List[DashboardSummaryItem]): List of trending workflows.
        system_health (List[DashboardSystemHealth]): List of system health statuses.
    """
    active_workflow_runs: int = Field(..., description="Number of currently active workflow runs.")
    completed_runs_today: int = Field(..., description="Number of completed runs today.")
    failed_runs_today: int = Field(..., description="Number of failed runs today.")
    total_mcp_definitions: int = Field(..., description="Total number of MCP definitions.")
    total_workflow_definitions: int = Field(..., description="Total number of workflow definitions.")
    recent_components: List[DashboardSummaryItem] = Field(default_factory=list, description="List of recent components.")
    trending_workflows: List[DashboardSummaryItem] = Field(default_factory=list, description="List of trending workflows.")
    system_health: List[DashboardSystemHealth] = Field(default_factory=list, description="List of system health statuses.")
