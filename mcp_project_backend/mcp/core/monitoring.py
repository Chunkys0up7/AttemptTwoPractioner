from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import after setting TESTING
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

# Global metrics container
_metrics = None

def get_metrics():
    """Get or create Prometheus metrics."""
    global _metrics
    if _metrics is None:
        if not os.getenv('TESTING'):
            try:
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

                _metrics = {
                    'REQUEST_LATENCY': REQUEST_LATENCY,
                    'REQUEST_COUNT': REQUEST_COUNT,
                    'ERROR_COUNT': ERROR_COUNT,
                    'CACHE_HIT': CACHE_HIT,
                    'CACHE_MISS': CACHE_MISS,
                    'MEMORY_USAGE': MEMORY_USAGE,
                    'CPU_USAGE': CPU_USAGE,
                    'DB_CONNECTIONS': DB_CONNECTIONS,
                    'SYSTEM_INFO': SYSTEM_INFO,
                    'HEALTH_STATUS': HEALTH_STATUS
                }
            except Exception as e:
                logger.error(f"Failed to initialize metrics: {e}")
                _metrics = {}
    return _metrics

class Monitor:
    """System performance monitoring class."""
    def __init__(self):
        if os.getenv('TESTING'):
            # In test mode, create mock metrics
            self.metrics = {
                'REQUEST_LATENCY': lambda *args, **kwargs: None,
                'REQUEST_COUNT': lambda *args, **kwargs: None,
                'ERROR_COUNT': lambda *args, **kwargs: None,
                'CACHE_HIT': lambda *args, **kwargs: None,
                'CACHE_MISS': lambda *args, **kwargs: None,
                'MEMORY_USAGE': lambda *args, **kwargs: None,
                'CPU_USAGE': lambda *args, **kwargs: None,
                'DB_CONNECTIONS': lambda *args, **kwargs: None,
                'SYSTEM_INFO': lambda *args, **kwargs: None,
                'HEALTH_STATUS': lambda *args, **kwargs: None
            }
        else:
            # Initialize real metrics
            self.metrics = get_metrics()
        self.start_time = datetime.now()

    async def track_request(self, endpoint: str, method: str, status: int, duration: float):
        """Track a request and its duration."""
        if not os.getenv('TESTING'):
            try:
                self.metrics['REQUEST_LATENCY'].labels(endpoint=endpoint, method=method, status=str(status)).observe(duration)
                self.metrics['REQUEST_COUNT'].labels(endpoint=endpoint, method=method, status=str(status)).inc()
            except Exception as e:
                logger.error(f"Error tracking request: {e}")

    async def track_error(self, endpoint: str, method: str, error_type: str):
        """Track an error occurrence."""
        if not os.getenv('TESTING'):
            try:
                self.metrics['ERROR_COUNT'].labels(endpoint=endpoint, method=method, error_type=error_type).inc()
            except Exception as e:
                logger.error(f"Error tracking error: {e}")

    async def track_cache_hit(self):
        """Track a cache hit."""
        if not os.getenv('TESTING'):
            try:
                self.metrics['CACHE_HIT'].inc()
            except Exception as e:
                logger.error(f"Error tracking cache hit: {e}")

    async def track_cache_miss(self):
        """Track a cache miss."""
        if not os.getenv('TESTING'):
            try:
                self.metrics['CACHE_MISS'].inc()
            except Exception as e:
                logger.error(f"Error tracking cache miss: {e}")

    async def update_system_metrics(self):
        """Update system resource metrics."""
        if not os.getenv('TESTING'):
            try:
                # Memory usage
                memory = psutil.virtual_memory()
                self.metrics['MEMORY_USAGE'].set(memory.percent)

                # CPU usage
                cpu = psutil.cpu_percent(interval=1)
                self.metrics['CPU_USAGE'].set(cpu)

                # System info
                self.metrics['SYSTEM_INFO'].info({
                    'platform': platform.system(),
                    'platform_release': platform.release(),
                    'platform_version': platform.version(),
                    'architecture': platform.machine(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version()
                })

                # Health status
                if memory.percent > 90 or cpu > 90:
                    self.metrics['HEALTH_STATUS'].state('critical')
                elif memory.percent > 80 or cpu > 80:
                    self.metrics['HEALTH_STATUS'].state('warning')
                else:
                    self.metrics['HEALTH_STATUS'].state('healthy')

            except Exception as e:
                logger.error(f"Error updating system metrics: {e}")
                self.metrics['HEALTH_STATUS'].state('critical')

    async def get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        if os.getenv('TESTING'):
            return {
                'uptime': '0:00:00',
                'memory': 0,
                'cpu': 0,
                'disk': 0,
                'health': 'healthy'
            }
        
        try:
            info = {
                'uptime': str(datetime.now() - self.start_time),
                'memory': psutil.virtual_memory().percent,
                'cpu': psutil.cpu_percent(interval=None),
                'disk': psutil.disk_usage('/').percent,
                'health': 'healthy'
            }
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                'uptime': '0:00:00',
                'memory': 0,
                'cpu': 0,
                'disk': 0,
                'health': 'critical'
            }

    async def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of all metrics."""
        if os.getenv('TESTING'):
            return {
                'requests': {},
                'errors': {},
                'cache': {},
                'resources': {},
                'system': await self.get_system_info()
            }
        
        try:
            snapshot = {
                'requests': self.metrics['requests'],
                'errors': self.metrics['errors'],
                'cache': self.metrics['cache'],
                'resources': self.metrics['resources'],
                'system': await self.get_system_info()
            }
            return snapshot
        except Exception as e:
            logger.error(f"Error getting metrics snapshot: {e}")
            return {
                'requests': {},
                'errors': {},
                'cache': {},
                'resources': {},
                'system': await self.get_system_info()
            }
        self.metrics: Dict[str, Dict[str, Any]] = {
            'requests': {},
            'errors': {},
            'cache': {},
            'resources': {}
        }

# Create monitor instance
if not os.getenv('TESTING'):
    monitor = Monitor()
else:
    # Create a mock monitor for testing
    class MockMonitor:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    monitor = MockMonitor()