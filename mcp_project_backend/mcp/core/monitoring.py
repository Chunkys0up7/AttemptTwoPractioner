from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from mcp.core.config import settings
import asyncio
from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    Enum, Info
)
import logging
import psutil
import platform
from sqlalchemy.ext.asyncio import AsyncSession

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics

# Request Metrics
REQUEST_LATENCY = Histogram(
    'workflow_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint', 'method', 'status']
)

REQUEST_COUNT = Counter(
    'workflow_requests_total',
    'Total number of requests',
    ['endpoint', 'method', 'status']
)

ERROR_COUNT = Counter(
    'workflow_errors_total',
    'Total number of errors',
    ['endpoint', 'method', 'error_type']
)

CACHE_HIT = Counter(
    'workflow_cache_hits_total',
    'Total number of cache hits'
)

CACHE_MISS = Counter(
    'workflow_cache_misses_total',
    'Total number of cache misses'
)

# Resource Metrics
MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

DB_CONNECTIONS = Gauge(
    'database_connections',
    'Number of active database connections'
)

SYSTEM_INFO = Info(
    'system_info',
    'System information'
)

HEALTH_STATUS = Enum(
    'system_health_status',
    'System health status',
    states=['healthy', 'warning', 'critical']
)

class Monitor:
    """
    System performance monitoring class.
    
    This class provides comprehensive monitoring capabilities including:
    - Request metrics (latency, count, errors)
    - Cache metrics (hits, misses, hit ratio)
    - Resource metrics (memory, CPU, database)
    - Health checks and alerts
    
    Attributes:
        start_time: System start time
        metrics: In-memory metrics storage
    """
    
    def __init__(self):
        """Initialize the monitor with system information."""
        self.start_time = datetime.now()
        self.metrics: Dict[str, Dict[str, Any]] = {
            'requests': {},
            'errors': {},
            'cache': {},
            'resources': {}
        }
        
        # Initialize system info
        SYSTEM_INFO.info({
            'hostname': platform.node(),
            'os': platform.system(),
            'python_version': platform.python_version()
        })

    async def record_request(
        self,
        endpoint: str,
        method: str,
        status: int,
        duration: float,
        cache_hit: bool = False
    ) -> None:
        """
        Record request metrics.

        Args:
            endpoint: API endpoint
            method: HTTP method
            status: HTTP status code
            duration: Request duration in seconds
            cache_hit: Whether the request was cached
        """
        REQUEST_COUNT.labels(endpoint, method, str(status)).inc()
        REQUEST_LATENCY.labels(endpoint, method, str(status)).observe(duration)

        if cache_hit:
            CACHE_HIT.inc()
        else:
            CACHE_MISS.inc()

    async def record_error(
        self,
        endpoint: str,
        method: str,
        error_type: str
    ) -> None:
        """
        Record error metrics.

        Args:
            endpoint: API endpoint
            method: HTTP method
            error_type: Type of error
        """
        ERROR_COUNT.labels(endpoint, method, error_type).inc()

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get system health status.

        Returns:
            Dictionary containing health metrics
        """
        uptime = datetime.now() - self.start_time
        return {
            'uptime': str(uptime),
            'requests': {
                'total': REQUEST_COUNT._value.get(),
                'cache_hit_ratio': CACHE_HIT._value.get() / 
                (CACHE_HIT._value.get() + CACHE_MISS._value.get())
            },
            'errors': {
                'total': ERROR_COUNT._value.get()
            }
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics.
        
        Returns:
            Dictionary containing all system metrics
        """
        try:
            # Get system resource metrics
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            
            return {
                'requests': {
                    'count': REQUEST_COUNT._value.get(),
                    'latency': REQUEST_LATENCY._sum.get() / REQUEST_LATENCY._count.get()
                },
                'cache': {
                    'hits': CACHE_HIT._value.get(),
                    'misses': CACHE_MISS._value.get(),
                    'hit_ratio': CACHE_HIT._value.get() / 
                    (CACHE_HIT._value.get() + CACHE_MISS._value.get())
                },
                'errors': {
                    'total': ERROR_COUNT._value.get()
                },
                'resources': {
                    'memory': memory.percent,
                    'cpu': cpu,
                    'disk': psutil.disk_usage('/').percent
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return {
                'error': str(e)
            }

    async def check_thresholds(self) -> List[str]:
        """
        Check all performance metrics against thresholds and return alerts.
        
        Returns:
            List of alert messages if thresholds are exceeded
        """
        try:
            metrics = await self.get_metrics()
            alerts = []
            
            # Request metrics
            try:
                latency = metrics['requests']['latency']
                if latency > settings.REQUEST_LATENCY_THRESHOLD:
                    alerts.append(f"High request latency: {latency:.2f}s (threshold: {settings.REQUEST_LATENCY_THRESHOLD}s)")
                    HEALTH_STATUS.state('warning')
            except Exception as e:
                logger.error(f"Error checking request latency: {str(e)}")
            
            # Cache metrics
            try:
                hit_ratio = metrics['cache']['hit_ratio']
                if hit_ratio < settings.CACHE_HIT_RATIO_THRESHOLD:
                    alerts.append(f"Low cache hit ratio: {hit_ratio:.2%} (threshold: {settings.CACHE_HIT_RATIO_THRESHOLD:.2%})")
                    HEALTH_STATUS.state('warning')
            except Exception as e:
                logger.error(f"Error checking cache metrics: {str(e)}")
            
            # Error rate
            try:
                error_count = metrics['errors']['total']
                request_count = metrics['requests']['count']
                if request_count > 0:
                    error_rate = error_count / request_count
                    if error_rate > settings.ERROR_RATE_THRESHOLD:
                        alerts.append(f"High error rate: {error_rate:.2%} (threshold: {settings.ERROR_RATE_THRESHOLD:.2%})")
                        HEALTH_STATUS.state('warning')
            except Exception as e:
                logger.error(f"Error calculating error rate: {str(e)}")
            
            # Resource metrics
            try:
                memory_usage = metrics['resources']['memory']
                if memory_usage > settings.MEMORY_THRESHOLD:
                    alerts.append(f"High memory usage: {memory_usage:.2%} (threshold: {settings.MEMORY_THRESHOLD:.2%})")
                    HEALTH_STATUS.state('critical')
            except Exception as e:
                logger.error(f"Error checking memory usage: {str(e)}")
            
            try:
                cpu_usage = metrics['resources']['cpu']
                if cpu_usage > settings.CPU_THRESHOLD:
                    alerts.append(f"High CPU usage: {cpu_usage:.2%} (threshold: {settings.CPU_THRESHOLD:.2%})")
                    HEALTH_STATUS.state('critical')
            except Exception as e:
                logger.error(f"Error checking CPU usage: {str(e)}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking thresholds: {str(e)}")
            HEALTH_STATUS.state('critical')
            return [f"System error: {str(e)}"]

    def reset_metrics(self) -> None:
        """
        Reset all in-memory metrics (for retention/cleanup).
        """
        REQUEST_COUNT._value.set(0)
        REQUEST_LATENCY._sum.set(0)
        REQUEST_LATENCY._count.set(0)
        ERROR_COUNT._value.set(0)
        CACHE_HIT._value.set(0)
        CACHE_MISS._value.set(0)
        self.start_time = datetime.now()

# Create monitor instance
monitor = Monitor()

# Periodic cleanup task (runs every 24 hours)
async def periodic_metric_cleanup():
    while True:
        await asyncio.sleep(60 * 60 * 24)  # 24 hours
        monitor.reset_metrics()
        logger.info("Performance metrics reset (in-memory cleanup)")

# To start the cleanup task, call:
# asyncio.create_task(periodic_metric_cleanup())
