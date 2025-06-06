"""
API Endpoints for dashboard-related data.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# from typing import List, Optional # Unused
# import uuid # Unused
# from datetime import datetime, timedelta # Unused

from mcp.db.session import get_db
from mcp.core.services.dashboard_service import DashboardService
from mcp.core.config import settings  # For API prefix
# Define a Pydantic model for the summary response for better OpenAPI documentation
from pydantic import BaseModel
from mcp.api.services.data_visualization_service import router as data_visualization_router


class DashboardSummaryResponse(BaseModel):
    total_mcp_definitions: int
    total_mcp_versions: int
    total_workflow_runs: int
    active_workflow_runs: int
    successful_runs_today: int
    failed_runs_today: int
    # Add other fields as needed, e.g.:
    # recent_mcp_definitions: List[str]


router = APIRouter(
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["Dashboard"],
)

# Dependency to get DashboardService instance


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retrieve a summary of data for the main dashboard.

    This includes counts of MCP definitions, versions, workflow runs (total, active, status for today),
    and potentially other relevant system statistics.
    """
    try:
        summary_data = await service.get_dashboard_summary()
        return DashboardSummaryResponse(**summary_data)
    except Exception as e:
        # Log the exception e
        # import logging
        # logging.getLogger(__name__).error(f"Error fetching dashboard summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the dashboard summary: {str(e)}"
        )

# Include visualization endpoints under the dashboard API
router.include_router(data_visualization_router, prefix="/visualization", tags=["Visualization"])

# Example chart config endpoint (static config for now)
from fastapi import Response

@router.get("/chart-config")
def get_chart_config():
    """
    Returns chart configuration options for the dashboard frontend.
    """
    try:
        config = {
            "type": "bar",
            "options": {
                "responsive": True,
                "plugins": {"legend": {"position": "top"}, "title": {"display": True, "text": "Workflow Run Status"}}
            },
            "data": {
                "labels": [],  # To be filled by /visualization/chart
                "datasets": [
                    {"label": "Runs", "data": [], "backgroundColor": "#36a2eb"}
                ]
            }
        }
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart config: {e}")

# Placeholder for real-time updates (to be implemented with WebSocket in a later phase)
# from fastapi import WebSocket
# @router.websocket("/ws/dashboard-updates")
# async def dashboard_updates(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         # Send updates (e.g., summary, chart data) in real time
#         await websocket.send_json({"type": "update", "data": ...})
#         await asyncio.sleep(2)
