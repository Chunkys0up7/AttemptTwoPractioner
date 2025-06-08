"""
API Endpoints for dashboard-related data.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import logging
from datetime import datetime
from mcp.db.session import get_db
from mcp.core.services.dashboard_service import DashboardService
from mcp.core.config import settings
from mcp.monitoring.performance import performance_monitor
from pydantic import BaseModel
from mcp.api.services.data_visualization_service import router as data_visualization_router
import asyncio
import uuid

logger = logging.getLogger(__name__)

class DashboardSummaryResponse(BaseModel):
    total_mcp_definitions: int
    total_mcp_versions: int
    total_workflow_runs: int
    active_workflow_runs: int
    successful_runs_today: int
    failed_runs_today: int
    recent_mcp_definitions: List[str]
    recent_workflow_runs: List[str]
    system_uptime: str
    memory_usage: float
    cpu_usage: float

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["Dashboard"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"}
    }
)

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """
    Dependency for DashboardService with error handling.
    """
    try:
        return DashboardService(db)
    except Exception as e:
        logger.error(f"Failed to initialize DashboardService: {e}")
        performance_monitor.increment_error("dashboard_service_init", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize dashboard service"
        )

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retrieve a comprehensive summary of data for the main dashboard.

    Security:
    - Requires authentication (TODO)
    - Rate limited to 60 requests per minute

    Returns:
    - 200: Dashboard summary data
    - 401: Unauthorized
    - 403: Forbidden
    - 500: Internal server error
    """
    try:
        with performance_monitor.monitor_dashboard_query("summary"):
            summary_data = await service.get_dashboard_summary()
            
        logger.info(
            f"[Request {request.state.request_id}] Retrieved dashboard summary"
        )
        
        return DashboardSummaryResponse(**summary_data)
        
    except SQLAlchemyError as e:
        logger.error(f"[Request {request.state.request_id}] Database error: {e}")
        performance_monitor.increment_error("dashboard_db_error", str(e))
        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Unexpected error: {e}")
        performance_monitor.increment_error("dashboard_unexpected_error", str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

@router.get("/chart-config", response_model=dict)
async def get_chart_config(
    request: Request,
    chart_type: Optional[str] = None,
    time_range: Optional[str] = "24h"
):
    """
    Returns chart configuration options for the dashboard frontend.

    Security:
    - Requires authentication (TODO)
    - Rate limited to 100 requests per minute

    Returns:
    - 200: Chart configuration
    - 400: Invalid parameters
    - 401: Unauthorized
    - 403: Forbidden
    - 500: Internal server error
    """
    try:
        if time_range not in ["1h", "24h", "7d", "30d"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid time range. Must be one of: 1h, 24h, 7d, 30d"
            )
            
        config = {
            "type": chart_type or "bar",
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "top"},
                    "title": {
                        "display": True,
                        "text": f"Workflow Run Status ({time_range})"
                    }
                }
            },
            "data": {
                "labels": [],  # To be filled by /visualization/chart
                "datasets": [
                    {
                        "label": "Runs",
                        "data": [],
                        "backgroundColor": "#36a2eb"
                    }
                ]
            }
        }
        
        logger.info(
            f"[Request {request.state.request_id}] Generated chart config for {time_range}"
        )
        
        return config
        
    except ValueError as e:
        logger.error(f"[Request {request.state.request_id}] Invalid parameter: {e}")
        performance_monitor.increment_error("dashboard_config_error", str(e))
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Unexpected error: {e}")
        performance_monitor.increment_error("dashboard_unexpected_error", str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

@router.websocket("/ws/dashboard-updates")
async def dashboard_updates(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates.

    Security:
    - Requires authentication (TODO)
    - Rate limited to 1 connection per client

    Returns:
    - WebSocket connection for real-time updates
    """
    await websocket.accept()
    try:
        # Initialize connection tracking
        connection_id = str(uuid.uuid4())
        logger.info(f"New dashboard updates connection: {connection_id}")
        
        while True:
            try:
                # TODO: Implement real dashboard update logic
                # For now, send periodic updates
                await websocket.send_json({
                    "type": "update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "status": "connected",
                        "connection_id": connection_id
                    }
                })
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"WebSocket error for {connection_id}: {e}")
                performance_monitor.increment_error("dashboard_ws_error", str(e))
                break
                
    finally:
        logger.info(f"Dashboard updates connection closed: {connection_id}")
        await websocket.close()

# Include visualization endpoints under the dashboard API
router.include_router(data_visualization_router, prefix="/visualization", tags=["Visualization"])
