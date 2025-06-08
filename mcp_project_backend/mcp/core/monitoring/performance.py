"""
Performance monitoring utilities for the MCP Backend.
"""
import logging
from datetime import datetime
from typing import Dict, Any
import prometheus_client
from prometheus_client import Counter, Histogram
from mcp.core.config import settings

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Performance monitoring class that tracks various metrics.
    """
    def __init__(self):
        self._initialized = False
        self._metrics = {}
        
    def start(self):
        """Initialize performance monitoring."""
        if self._initialized:
            return
            
        # Create metrics
        self._metrics["request_duration"] = Histogram(
            "mcp_request_duration_seconds",
            "Request duration in seconds",
            ["endpoint", "method"]
        )
        
        self._metrics["database_queries"] = Counter(
            "mcp_database_queries_total",
            "Total number of database queries",
            ["type", "status"]
        )
        
        self._metrics["cache_hits"] = Counter(
            "mcp_cache_hits_total",
            "Total number of cache hits",
            ["type"]
        )
        
        self._metrics["cache_misses"] = Counter(
            "mcp_cache_misses_total",
            "Total number of cache misses",
            ["type"]
        )
        
        self._initialized = True
        logger.info("Performance monitoring initialized")
        
    def stop(self):
        """Stop performance monitoring."""
        self._initialized = False
        logger.info("Performance monitoring stopped")
        
    def monitor_request(self, endpoint: str, method: str, duration: float):
        """
        Monitor a request's duration.
        
        Args:
            endpoint: The endpoint path
            method: HTTP method (GET, POST, etc.)
            duration: Request duration in seconds
        """
        if not self._initialized:
            return
            
        self._metrics["request_duration"].labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
        
    def monitor_database_query(self, query_type: str, success: bool):
        """
        Monitor a database query.
        
        Args:
            query_type: Type of query (e.g., SELECT, INSERT)
            success: Whether the query was successful
        """
        if not self._initialized:
            return
            
        status = "success" if success else "error"
        self._metrics["database_queries"].labels(
            type=query_type,
            status=status
        ).inc()
        
    def monitor_cache_operation(self, operation_type: str, hit: bool):
        """
        Monitor cache operations.
        
        Args:
            operation_type: Type of cache operation (e.g., GET, SET)
            hit: Whether it was a cache hit
        """
        if not self._initialized:
            return
            
        metric = "cache_hits" if hit else "cache_misses"
        self._metrics[metric].labels(
            type=operation_type
        ).inc()

# Global instance
performance_monitor = PerformanceMonitor()
