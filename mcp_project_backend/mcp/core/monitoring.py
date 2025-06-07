from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from mcp.core.config import settings
import asyncio
from prometheus_client import Counter, Histogram, Gauge, Summary
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
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

class Monitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics: Dict[str, Dict[str, Any]] = {
            'requests': {},
            'errors': {},
            'cache': {}
        }

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
        Get all collected metrics.

        Returns:
            Dictionary containing all metrics
        """
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
            }
        }

    async def check_thresholds(self) -> None:
        """
        Check performance metrics against thresholds and log alerts if exceeded.
        """
        metrics = await self.get_metrics()
        alerts = []
        # Request latency
        try:
            latency = metrics['requests']['latency']
            if latency > settings.REQUEST_LATENCY_THRESHOLD:
                alert = f"High request latency: {latency:.2f}s (threshold: {settings.REQUEST_LATENCY_THRESHOLD}s)"
                logger.warning(alert)
                alerts.append(alert)
        except Exception:
            pass
        # Cache hit ratio
        try:
            hit_ratio = metrics['cache']['hit_ratio']
            if hit_ratio < settings.CACHE_HIT_RATIO_THRESHOLD:
                alert = f"Low cache hit ratio: {hit_ratio:.2%} (threshold: {settings.CACHE_HIT_RATIO_THRESHOLD:.2%})"
                logger.warning(alert)
                alerts.append(alert)
        except Exception:
            pass
        # Error rate
        try:
            error_count = metrics['errors']['total']
            request_count = metrics['requests']['count']
            if request_count > 0:
                error_rate = error_count / request_count
                if error_rate > settings.ERROR_RATE_THRESHOLD:
                    alert = f"High error rate: {error_rate:.2%} (threshold: {settings.ERROR_RATE_THRESHOLD:.2%})"
                    logger.warning(alert)
                    alerts.append(alert)
        except Exception:
            pass
        return alerts

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
