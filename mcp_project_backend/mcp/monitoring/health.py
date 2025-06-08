"""
Health monitoring utilities for the MCP Backend.
"""
import logging
from typing import Dict, Any
import prometheus_client
from prometheus_client import Gauge
from mcp.core.config import settings

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    Health monitoring class that tracks system health metrics.
    """
    def __init__(self):
        self._initialized = False
        self._metrics = {}
        
    def start(self):
        """Initialize health monitoring."""
        if self._initialized:
            return
            
        # Create metrics
        self._metrics["system_uptime"] = Gauge(
            "mcp_health_system_uptime_seconds",
            "System uptime in seconds"
        )
        
        self._metrics["database_connection_status"] = Gauge(
            "mcp_health_database_connection_status",
            "Database connection status (1=healthy, 0=unhealthy)"
        )
        
        self._metrics["memory_usage"] = Gauge(
            "mcp_health_memory_usage_bytes",
            "Memory usage in bytes"
        )
        
        self._metrics["cpu_usage"] = Gauge(
            "mcp_health_cpu_usage_percent",
            "CPU usage percentage"
        )
        
        self._initialized = True
        logger.info("Health monitoring initialized")
        
    def stop(self):
        """Stop health monitoring."""
        self._initialized = False
        logger.info("Health monitoring stopped")
        
    def update_uptime(self, seconds: float):
        """
        Update system uptime.
        
        Args:
            seconds: Number of seconds since system start
        """
        if not self._initialized:
            return
            
        self._metrics["system_uptime"].set(seconds)
        
    def update_database_status(self, is_healthy: bool):
        """
        Update database connection status.
        
        Args:
            is_healthy: Whether the database connection is healthy
        """
        if not self._initialized:
            return
            
        self._metrics["database_connection_status"].set(1 if is_healthy else 0)
        
    def update_memory_usage(self, usage_bytes: int):
        """
        Update memory usage.
        
        Args:
            usage_bytes: Current memory usage in bytes
        """
        if not self._initialized:
            return
            
        self._metrics["memory_usage"].set(usage_bytes)
        
    def update_cpu_usage(self, usage_percent: float):
        """
        Update CPU usage.
        
        Args:
            usage_percent: Current CPU usage percentage (0-100)
        """
        if not self._initialized:
            return
            
        self._metrics["cpu_usage"].set(usage_percent)

# Global instance
health_monitor = HealthMonitor()
