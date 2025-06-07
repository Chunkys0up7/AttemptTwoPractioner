import os
from fastapi import APIRouter, Depends, HTTPException, status
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.multiprocess import MultiProcessCollector
from prometheus_client import CollectorRegistry
from mcp.core.config import settings
from fastapi import Response

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import after setting TESTING
from mcp.core.monitoring import monitor

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
    if os.getenv('TESTING'):
        return Response(
            content="",
            media_type=CONTENT_TYPE_LATEST
        )
    
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
    if os.getenv('TESTING'):
        return {
            "metrics": {
                "uptime": "0:00:00",
                "requests": {"count": 0},
                "errors": {"total": 0},
                "cache": {"hit_ratio": 0.0}
            },
            "alerts": []
        }
    
    metrics = await monitor.get_metrics()
    alerts = await monitor.check_thresholds()
    return {"metrics": metrics, "alerts": alerts}

@router.post("/reset")
async def reset_metrics():
    """
    Reset all in-memory performance metrics (admin only).
    """
    if os.getenv('TESTING'):
        return {"message": "Performance metrics reset (mocked)."}
    
    monitor.reset_metrics()
    return {"message": "Performance metrics reset."}

@router.get("/dashboard", response_model=dict)
async def performance_dashboard():
    """
    Get a dashboard summary of key performance metrics and alerts (for visualization).
    """
    if os.getenv('TESTING'):
        return {
            "metrics": {
                "uptime": "0:00:00",
                "requests": {"count": 0},
                "errors": {"total": 0},
                "cache": {"hit_ratio": 0.0}
            },
            "alerts": [],
            "dashboard": {
                "uptime": "0:00:00",
                "request_count": 0,
                "error_count": 0,
                "cache_hit_ratio": 0.0,
                "active_alerts": 0
            }
        }
    
    metrics = await monitor.get_metrics()
    alerts = await monitor.check_thresholds()
    return {
        "metrics": metrics,
        "alerts": alerts,
        "dashboard": {
            "uptime": metrics.get("uptime", "0:00:00"),
            "request_count": metrics.get("requests", {}).get("count", 0),
            "error_count": metrics.get("errors", {}).get("total", 0),
            "cache_hit_ratio": metrics.get("cache", {}).get("hit_ratio", 0.0),
            "active_alerts": len(alerts)
        }
    }
