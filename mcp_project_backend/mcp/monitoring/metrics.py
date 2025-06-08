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
    Metrics monitoring class that tracks various system metrics.
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
        
        self._metrics["api_request_duration"] = Histogram(
            "mcp_api_request_duration_seconds",
            "API request duration in seconds",
            ["endpoint", "method"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self._metrics["database_queries"] = Counter(
            "mcp_database_queries_total",
            "Total number of database queries",
            ["type", "status"]
        )
        
        self._metrics["database_query_duration"] = Histogram(
            "mcp_database_query_duration_seconds",
            "Database query duration in seconds",
            ["type"],
            buckets=[0.01, 0.1, 0.5, 1.0, 2.0, 5.0]
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
        logger.info("Metrics monitoring initialized")
        
    def stop(self):
        """Stop metrics monitoring."""
        self._initialized = False
        logger.info("Metrics monitoring stopped")
        
    def increment_api_request(self, endpoint: str, method: str, status: str):
        """
        Track an API request.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            status: HTTP status code
        """
        if not self._initialized:
            return
            
        self._metrics["api_requests"].labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
    def observe_api_duration(self, endpoint: str, method: str, duration: float):
        """
        Track API request duration.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            duration: Request duration in seconds
        """
        if not self._initialized:
            return
            
        self._metrics["api_request_duration"].labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
        
    def increment_database_query(self, query_type: str, success: bool):
        """
        Track a database query.
        
        Args:
            query_type: Type of query (e.g., SELECT, INSERT)
            success: Whether the query was successful
        """
        if not self._initialized:
            return
            
        status = "success" if success else "failure"
        self._metrics["database_queries"].labels(
            type=query_type,
            status=status
        ).inc()
        
    def observe_query_duration(self, query_type: str, duration: float):
        """
        Track database query duration.
        
        Args:
            query_type: Type of query
            duration: Query duration in seconds
        """
        if not self._initialized:
            return
            
        self._metrics["database_query_duration"].labels(
            type=query_type
        ).observe(duration)
        
    def increment_cache_hit(self, cache_type: str):
        """
        Track a cache hit.
        
        Args:
            cache_type: Type of cache (e.g., in-memory, redis)
        """
        if not self._initialized:
            return
            
        self._metrics["cache_hits"].labels(
            type=cache_type
        ).inc()
        
    def increment_cache_miss(self, cache_type: str):
        """
        Track a cache miss.
        
        Args:
            cache_type: Type of cache
        """
        if not self._initialized:
            return
            
        self._metrics["cache_misses"].labels(
            type=cache_type
        ).inc()

# Global instance
metrics_monitor = MetricsMonitor()
