from fastapi import APIRouter, Depends
from mcp.core.observability.metrics_service import aimetrics_service
from mcp.api.routers.auth_routes import require_role
from mcp.db.models.user import User
from typing import Optional, Dict

router = APIRouter()

@router.post("/metrics/performance")
def log_performance(model_name: str, latency_ms: float, accuracy: float, extra: Optional[Dict] = None, current_user: User = Depends(require_role("Admin"))):
    aimetrics_service.log_performance(model_name, latency_ms, accuracy, extra)
    return {"detail": "Performance metrics logged"}

@router.post("/metrics/custom")
def log_custom_metric(name: str, value: float, tags: Optional[Dict] = None, current_user: User = Depends(require_role("Admin"))):
    aimetrics_service.log_custom_metric(name, value, tags)
    return {"detail": "Custom metric logged"} 