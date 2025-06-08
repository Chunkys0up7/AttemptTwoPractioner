"""
Health monitoring utilities for the MCP Backend.
"""
import logging
from typing import Dict, Any
import prometheus_client
from prometheus_client import Gauge
from mcp.core.config import settings
import asyncio

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    Health monitoring class that tracks system health metrics.
    """
    def __init__(self):
        self._initialized = False
        self._metrics = {}
        self._health_checks = {}
        
    def start(self):
        """Initialize health monitoring."""
        if self._initialized:
            return
            
        # Create metrics
        self._metrics["service_status"] = Gauge(
            "mcp_service_status",
            "Service health status",
            ["service", "status"]
        )
        
        self._metrics["resource_usage"] = Gauge(
            "mcp_resource_usage_percent",
            "Resource usage percentage",
            ["resource", "type"]
        )
        
        self._metrics["queue_length"] = Gauge(
            "mcp_queue_length",
            "Length of processing queues",
            ["queue"]
        )
        
        self._initialized = True
        logger.info("Health monitoring initialized")
        
    def stop(self):
        """Stop health monitoring."""
        self._initialized = False
        logger.info("Health monitoring stopped")
        
    def register_health_check(self, name: str, check_func: callable):
        """
        Register a health check function.
        
        Args:
            name: Name of the health check
            check_func: Function that performs the health check
        """
        if not self._initialized:
            return
            
        self._health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")
        
    async def check_health(self) -> Dict[str, Any]:
        """
        Perform all registered health checks.
        
        Returns:
            Dict containing health check results
        """
        if not self._initialized:
            return {"healthy": False, "error": "Health monitoring not initialized"}
            
        results = {"healthy": True, "checks": {}}
        
        for name, check_func in self._health_checks.items():
            try:
                result = await asyncio.wait_for(check_func(), timeout=5)
                results["checks"][name] = result
                if not result["healthy"]:
                    results["healthy"] = False
            except Exception as e:
                results["healthy"] = False
                results["checks"][name] = {
                    "healthy": False,
                    "error": str(e)
                }
                
        return results
        
    def update_resource_usage(self, resource: str, usage: float, resource_type: str):
        """
        Update resource usage metric.
        
        Args:
            resource: Name of the resource
            usage: Usage percentage (0-100)
            resource_type: Type of resource (e.g., "cpu", "memory")
        """
        if not self._initialized:
            return
            
        self._metrics["resource_usage"].labels(
            resource=resource,
            type=resource_type
        ).set(usage)
        
    def update_queue_length(self, queue_name: str, length: int):
        """
        Update queue length metric.
        
        Args:
            queue_name: Name of the queue
            length: Current queue length
        """
        if not self._initialized:
            return
            
        self._metrics["queue_length"].labels(
            queue=queue_name
        ).set(length)

# Global instance
health_monitor = HealthMonitor()
