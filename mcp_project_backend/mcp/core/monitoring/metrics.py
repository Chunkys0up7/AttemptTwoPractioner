"""
Metrics monitoring utilities for the MCP Backend.
"""
import logging
from typing import Dict, Any
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram
from mcp.core.config import settings

logger = logging.getLogger(__name__)

class MetricsMonitor:
    """
    Metrics monitoring class that tracks various application metrics.
    """
    def __init__(self):
        self._initialized = False
        self._metrics = {}
        
    def start(self):
        """Initialize metrics monitoring."""
        if self._initialized:
            return
            
        # Create metrics
        self._metrics["api_requests"] = Counter(
            "mcp_api_requests_total",
            "Total number of API requests",
            ["endpoint", "method", "status"]
        )
        
        self._metrics["api_errors"] = Counter(
            "mcp_api_errors_total",
            "Total number of API errors",
            ["type", "endpoint"]
        )
        
        self._metrics["workflow_executions"] = Counter(
            "mcp_workflow_executions_total",
            "Total number of workflow executions",
            ["status", "type"]
        )
        
        self._metrics["mcp_operations"] = Counter(
            "mcp_operations_total",
            "Total number of MCP operations",
            ["type", "status"]
        )
        
        self._metrics["request_duration"] = Histogram(
            "mcp_request_duration_seconds",
            "Request duration in seconds",
            ["endpoint", "method"]
        )
        
        self._metrics["system_uptime"] = Gauge(
            "mcp_system_uptime_seconds",
            "System uptime in seconds"
        )
        
        self._initialized = True
        logger.info("Metrics monitoring initialized")
        
    def stop(self):
        """Stop metrics monitoring."""
        self._initialized = False
        logger.info("Metrics monitoring stopped")
        
    def increment(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None):
        """
        Increment a counter metric.
        
        Args:
            metric_name: Name of the metric
            value: Value to increment by
            tags: Dictionary of tags to apply to the metric
        """
        if not self._initialized:
            return
            
        metric = self._metrics.get(metric_name)
        if not metric:
            logger.warning(f"Metric {metric_name} not found")
            return
            
        labels = {}
        if tags:
            labels.update(tags)
            
        metric.labels(**labels).inc(value)
        
    def observe(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """
        Observe a value for a histogram metric.
        
        Args:
            metric_name: Name of the metric
            value: Value to observe
            tags: Dictionary of tags to apply to the metric
        """
        if not self._initialized:
            return
            
        metric = self._metrics.get(metric_name)
        if not metric:
            logger.warning(f"Metric {metric_name} not found")
            return
            
        labels = {}
        if tags:
            labels.update(tags)
            
        metric.labels(**labels).observe(value)
        
    def set(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """
        Set a gauge metric to a specific value.
        
        Args:
            metric_name: Name of the metric
            value: Value to set
            tags: Dictionary of tags to apply to the metric
        """
        if not self._initialized:
            return
            
        metric = self._metrics.get(metric_name)
        if not metric:
            logger.warning(f"Metric {metric_name} not found")
            return
            
        labels = {}
        if tags:
            labels.update(tags)
            
        metric.labels(**labels).set(value)

# Global instance
metrics_monitor = MetricsMonitor()
