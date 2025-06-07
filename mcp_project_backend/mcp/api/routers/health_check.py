from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from mcp.db.session import get_db
from mcp.core.config import settings
from mcp.core.monitoring import monitor
from typing import Dict, Any
import asyncio
from datetime import datetime
import redis
import json

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/health",
    tags=["Health Check"]
)

class HealthStatus:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )

    async def check_database(self, db: Session) -> Dict[str, Any]:
        """
        Check database health.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing database health status
        """
        try:
            # Test database connection
            db.execute("SELECT 1").scalar()
            return {
                "status": "healthy",
                "details": {
                    "last_check": datetime.now().isoformat(),
                    "error": None
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {
                    "last_check": datetime.now().isoformat(),
                    "error": str(e)
                }
            }

    async def check_redis(self) -> Dict[str, Any]:
        """
        Check Redis health.
        
        Returns:
            Dictionary containing Redis health status
        """
        try:
            # Test Redis connection
            self.redis_client.ping()
            return {
                "status": "healthy",
                "details": {
                    "last_check": datetime.now().isoformat(),
                    "error": None
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {
                    "last_check": datetime.now().isoformat(),
                    "error": str(e)
                }
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.
        
        Returns:
            Dictionary containing system health status
        """
        try:
            # Get metrics from monitor
            metrics = await monitor.get_metrics()
            # Get health status from monitor
            health = await monitor.get_health_status()
            # Check for performance alerts
            alerts = await monitor.check_thresholds()
            return {
                "status": "healthy",
                "details": {
                    "version": settings.VERSION,
                    "uptime": health['uptime'],
                    "metrics": metrics,
                    "health": health,
                    "alerts": alerts
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {
                    "last_check": datetime.now().isoformat(),
                    "error": str(e)
                }
            }

@router.get("/", response_model=Dict[str, Any])
async def health_check(
    db: Session = Depends(get_db)
):
    """
    Get system health status.
    
    Returns:
        Dictionary containing health status of all system components
    """
    health_status = HealthStatus()
    
    # Check database
    db_status = await health_status.check_database(db)
    
    # Check Redis
    redis_status = await health_status.check_redis()
    
    # Get system status
    system_status = await health_status.get_system_status()
    
    # Determine overall status
    overall_status = "healthy"
    if any(
        status["status"] == "unhealthy"
        for status in [db_status, redis_status, system_status]
    ):
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "components": {
            "database": db_status,
            "redis": redis_status,
            "system": system_status
        },
        "timestamp": datetime.now().isoformat()
    }
