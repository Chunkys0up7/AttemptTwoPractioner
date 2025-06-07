from fastapi import APIRouter, Depends, HTTPException, status
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.multiprocess import MultiProcessCollector
from prometheus_client import CollectorRegistry
from mcp.core.config import settings
from mcp.core.monitoring import monitor
from fastapi import Response

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/metrics",
    tags=["Metrics"]
)

@router.get("/", response_class=Response)
async def metrics():
    """
    Get Prometheus metrics.
    
    Returns:
        Prometheus metrics in text format
    """
    registry = CollectorRegistry()
    MultiProcessCollector(registry)
    
    metrics = generate_latest(registry)
    
    return Response(
        content=metrics,
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/report", response_model=dict)
async def performance_report():
    """
    Get a summary performance report (key metrics and alerts).
    """
    metrics = await monitor.get_metrics()
    alerts = await monitor.check_thresholds()
    return {"metrics": metrics, "alerts": alerts}

@router.post("/reset")
async def reset_metrics():
    """
    Reset all in-memory performance metrics (admin only).
    """
    monitor.reset_metrics()
    return {"message": "Performance metrics reset."}
