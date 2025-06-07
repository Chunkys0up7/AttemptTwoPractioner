from typing import Dict, Any, Optional, Callable, TypeVar, Generic, List, Tuple
from datetime import datetime, timedelta
import asyncio
from prometheus_client import Gauge, Counter, Histogram, Summary, Enum
from mcp.core.config import settings
import logging
from functools import wraps
from contextlib import contextmanager
import time
from sqlalchemy import text
import psutil

T = TypeVar('T')

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        # Request metrics
        self.request_latency = Histogram(
            'workflow_request_latency_seconds',
            'Request processing latency in seconds',
            ['endpoint', 'method', 'status', 'user_agent'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.request_count = Counter(
            'workflow_requests_total',
            'Total number of requests',
            ['endpoint', 'method', 'status', 'user_agent']
        )
        
        self.active_requests = Gauge(
            'workflow_active_requests',
            'Number of active requests',
            ['endpoint']
        )
        
        # Database metrics
        self.db_query_count = Counter(
            'workflow_db_queries_total',
            'Total number of database queries',
            ['query_type', 'table', 'operation']
        )
        
        self.db_query_latency = Histogram(
            'workflow_db_query_latency_seconds',
            'Database query latency in seconds',
            ['query_type', 'table', 'operation'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0]
        )
        
        self.db_query_errors = Counter(
            'workflow_db_query_errors_total',
            'Total number of database query errors',
            ['query_type', 'table', 'operation', 'error_type']
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'workflow_cache_hits_total',
            'Total number of cache hits'
        )
        
        self.cache_misses = Counter(
            'workflow_cache_misses_total',
            'Total number of cache misses'
        )
        
        self.cache_latency = Histogram(
            'workflow_cache_latency_seconds',
            'Cache operation latency in seconds',
            ['operation'],
            buckets=[0.0001, 0.001, 0.01, 0.1]
        )
        
        self.cache_size = Gauge(
            'workflow_cache_size_bytes',
            'Cache size in bytes',
            ['operation']
        )
        
        # Workflow execution metrics
        self.workflow_executions = Counter(
            'workflow_executions_total',
            'Total number of workflow executions',
            ['workflow_id', 'status']
        )
        
        self.workflow_execution_latency = Histogram(
            'workflow_execution_latency_seconds',
            'Workflow execution latency in seconds',
            ['workflow_id', 'status']
        )
        
        self.workflow_step_executions = Counter(
            'workflow_step_executions_total',
            'Total number of workflow step executions',
            ['workflow_id', 'step_id', 'status']
        )
        
        self.workflow_step_latency = Histogram(
            'workflow_step_latency_seconds',
            'Workflow step execution latency in seconds',
            ['workflow_id', 'step_id', 'status']
        )
        
        # System health metrics
        self.system_uptime = Gauge(
            'workflow_system_uptime_seconds',
            'System uptime in seconds'
        )
        
        self.memory_usage = Gauge(
            'workflow_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage = Gauge(
            'workflow_cpu_usage_percent',
            'CPU usage percentage'
        )
        
        # Error metrics
        self.errors_total = Counter(
            'workflow_errors_total',
            'Total number of errors',
            ['error_type', 'source']
        )
        
        self.error_rate = Gauge(
            'workflow_error_rate',
            'Error rate per second',
            ['error_type', 'source']
        )
        
        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            'workflow_rate_limit_hits_total',
            'Total number of rate limit hits',
            ['endpoint', 'user_id']
        )
        
        self.rate_limit_exceeded = Counter(
            'workflow_rate_limit_exceeded_total',
            'Total number of rate limit exceeded events',
            ['endpoint', 'user_id']
        )
        
        # Authentication metrics
        self.auth_attempts = Counter(
            'workflow_auth_attempts_total',
            'Total number of authentication attempts',
            ['status', 'method']
        )
        
        self.auth_latency = Histogram(
            'workflow_auth_latency_seconds',
            'Authentication latency in seconds',
            ['status', 'method']
        )
        
        # Health status
        self.health_status = Enum(
            'workflow_health_status',
            'Health status of the system',
            states=['healthy', 'degraded', 'unhealthy']
        )
        
        # Initialize system metrics
        self.last_update = datetime.utcnow()
        self.update_system_metrics()
        
        # Start periodic updates
        asyncio.create_task(self._periodic_updates())

    async def _periodic_updates(self):
        """Periodically update system metrics."""
        while True:
            self.update_system_metrics()
            await asyncio.sleep(10)

    def update_system_metrics(self):
        """Update system-level metrics."""
        self.system_uptime.set((datetime.utcnow() - self.last_update).total_seconds())
        self.memory_usage.set(psutil.virtual_memory().percent)
        self.cpu_usage.set(psutil.cpu_percent())

    @contextmanager
    def monitor_request(self, endpoint: str, method: str, user_agent: str = ''):
        """
        Context manager for monitoring HTTP requests.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            user_agent: User agent string
        """
        start_time = time.time()
        status = "200"
        self.active_requests.labels(endpoint).inc()
        try:
            yield
        except Exception as e:
            status = "500"
            error_type = type(e).__name__
            self.increment_error("request", f"{endpoint}:{method}:{error_type}")
            self.error_rate.labels("request", f"{endpoint}:{method}").inc()
            raise
        finally:
            duration = time.time() - start_time
            self.request_latency.labels(endpoint, method, status, user_agent).observe(duration)
            self.request_count.labels(endpoint, method, status, user_agent).inc()
            self.active_requests.labels(endpoint).dec()

    @contextmanager
    def monitor_db_query(self, query_type: str, table: str, operation: str):
        """
        Context manager for monitoring database queries.
        
        Args:
            query_type: Type of query (e.g., 'SELECT', 'INSERT')
            table: Table being queried
            operation: Operation type (e.g., 'read', 'write')
        """
        start_time = time.time()
        try:
            yield
        except Exception as e:
            error_type = type(e).__name__
            self.db_query_errors.labels(query_type, table, operation, error_type).inc()
            self.increment_error("db_query", f"{query_type}:{table}:{operation}")
            raise
        finally:
            duration = time.time() - start_time
            self.db_query_count.labels(query_type, table, operation).inc()
            self.db_query_latency.labels(query_type, table, operation).observe(duration)

    @contextmanager
    def monitor_cache_operation(self, operation: str, hit: bool = False, size: Optional[int] = None):
        """
        Context manager for monitoring cache operations.
        
        Args:
            operation: Cache operation type (e.g., 'get', 'set')
            hit: Whether the operation was a cache hit
            size: Cache size in bytes (optional)
        """
        start_time = time.time()
        try:
            yield
        except Exception as e:
            self.increment_error("cache", f"{operation}")
            raise
        finally:
            duration = time.time() - start_time
            self.cache_latency.labels(operation).observe(duration)
            if hit:
                self.cache_hits.inc()
            else:
                self.cache_misses.inc()
            if size:
                self.cache_size.labels(operation).observe(size)

    @contextmanager
    def monitor_workflow_execution(self, workflow_id: str):
        """
        Context manager for monitoring workflow executions.
        
        Args:
            workflow_id: ID of the workflow
        """
        start_time = time.time()
        status = "success"
        try:
            yield
        except Exception as e:
            status = "error"
            self.increment_error("workflow", workflow_id)
            raise
        finally:
            duration = time.time() - start_time
            self.workflow_executions.labels(workflow_id, status).inc()
            self.workflow_execution_latency.labels(workflow_id, status).observe(duration)

    @contextmanager
    def monitor_workflow_step(self, workflow_id: str, step_id: str):
        """
        Context manager for monitoring workflow steps.
        
        Args:
            workflow_id: ID of the workflow
            step_id: ID of the step
        """
        start_time = time.time()
        status = "success"
        try:
            yield
        except Exception as e:
            status = "error"
            self.increment_error("workflow_step", f"{workflow_id}:{step_id}")
            raise
        finally:
            duration = time.time() - start_time
            self.workflow_step_executions.labels(workflow_id, step_id, status).inc()
            self.workflow_step_latency.labels(workflow_id, step_id, status).observe(duration)

    def increment_error(self, error_type: str, error_message: str):
        """Increment error counter for a specific error type."""
        self.errors_total.labels(error_type, 'api').inc()
        self.error_rate.labels(error_type, 'api').inc()

    def check_rate_limit(self, key: str, limit: int, period: int) -> bool:
        """Check if a rate limit has been exceeded."""
        current_count = self.rate_limit_hits.labels(key).inc()
        if current_count > limit:
            self.rate_limit_exceeded.labels(key).inc()
            return False
        return True

    def update_health_status(self, component: str, status: str):
        """Update health status for a component."""
        self.health_status.state(status)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        metrics = {
            "uptime": self.system_uptime._value.get(),
            "requests": {
                "count": self.request_count._value.get(),
                "latency": self.request_latency._sum.get(),
                "active": self.active_requests._value.get()
            },
            "errors": {
                "total": self.errors_total._value.get(),
                "rate": self.error_rate._value.get()
            },
            "cache": {
                "hits": self.cache_hits._value.get(),
                "misses": self.cache_misses._value.get(),
                "hit_ratio": self.cache_hits._value.get() / max(1, self.cache_hits._value.get() + self.cache_misses._value.get())
            },
            "db": {
                "queries": self.db_query_count._value.get(),
                "latency": self.db_query_latency._sum.get(),
                "errors": self.db_query_errors._value.get()
            },
            "system": {
                "memory": self.memory_usage._value.get(),
                "cpu": self.cpu_usage._value.get()
            }
        }
        return metrics

    async def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check if any metrics exceed configured thresholds."""
        alerts = []
        
        # Check error rate
        error_rate = self.error_rate._value.get()
        if error_rate > settings.error_rate_threshold:
            alerts.append({
                "type": "error_rate",
                "severity": "high",
                "message": f"Error rate ({error_rate:.2f}) exceeds threshold ({settings.error_rate_threshold})",
                "value": error_rate,
                "threshold": settings.error_rate_threshold
            })
        
        # Check memory usage
        memory_usage = self.memory_usage._value.get()
        if memory_usage > settings.MEMORY_THRESHOLD:
            alerts.append({
                "type": "memory_usage",
                "severity": "high",
                "message": f"Memory usage ({memory_usage:.2f}%) exceeds threshold ({settings.MEMORY_THRESHOLD}%)",
                "value": memory_usage,
                "threshold": settings.memory_threshold
            })
        
        # Check CPU usage
        cpu_usage = self.cpu_usage._value.get()
        if cpu_usage > settings.cpu_threshold:
            alerts.append({
                "type": "cpu_usage",
                "severity": "high",
                "message": f"CPU usage ({cpu_usage:.2f}%) exceeds threshold ({settings.cpu_threshold}%)",
                "value": cpu_usage,
                "threshold": settings.cpu_threshold
            })
        
        return alerts

    async def get_dashboard(self) -> Dict[str, Any]:
        """Get a dashboard summary of key performance metrics and alerts."""
        metrics = await self.get_metrics()
        alerts = await self.check_thresholds()
        return {
            "metrics": metrics,
            "alerts": alerts,
            "dashboard": {
                "uptime": metrics.get("uptime"),
                "request_count": metrics["requests"]["count"],
                "error_count": metrics["errors"]["total"],
                "cache_hit_ratio": metrics["cache"]["hit_ratio"],
                "active_alerts": len(alerts)
            }
        }

    def monitor_auth_attempt(self, status: str, method: str):
        """
        Monitor authentication attempts.
        
        Args:
            status: Authentication status
            method: Authentication method
        """
        self.auth_attempts.labels(status, method).inc()

    def monitor_rate_limit(self, endpoint: str, user_id: str, exceeded: bool):
        """
        Monitor rate limiting events.
        
        Args:
            endpoint: API endpoint
            user_id: User ID
            exceeded: Whether rate limit was exceeded
        """
        if exceeded:
            self.rate_limit_exceeded.labels(endpoint, user_id).inc()
        else:
            self.rate_limit_hits.labels(endpoint, user_id).inc()

    def update_health_status(self, status: str):
        """
        Update system health status.
        
        Args:
            status: Health status ('healthy', 'degraded', 'unhealthy')
        """
        if status not in ['healthy', 'degraded', 'unhealthy']:
            raise ValueError(f"Invalid health status: {status}")
        self.health_status.state = status
        
        # Update related metrics
        if status == 'unhealthy':
            self.error_rate.labels('health', 'system').set(1.0)
        else:
            self.error_rate.labels('health', 'system').set(0.0)

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        try:
            return {
                'status': self.health_status.state,
                'metrics': {
                    'errors': self.errors_total._value.get(),
                    'error_rate': self.error_rate._value.get(),
                    'requests': self.request_count._value.get(),
                    'active_requests': self.active_requests._value.get(),
                    'db_queries': self.db_query_count._value.get(),
                    'cache_hits': self.cache_hits._value.get(),
                    'cache_misses': self.cache_misses._value.get(),
                    'cpu_usage': self.cpu_usage._value.get(),
                    'memory_usage': self.memory_usage._value.get(),
                    'uptime': self.system_uptime._value.get()
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving health status: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get all system metrics."""
        return {
            'uptime': self.system_uptime._value.get(),
            'memory_usage': self.memory_usage._value.get(),
            'cpu_usage': self.cpu_usage._value.get()
        }

    def get_workflow_metrics(self, workflow_id: str = None) -> Dict[str, Any]:
        """
        Get metrics for a specific workflow.
        
        Args:
            workflow_id: ID of the workflow (optional)
        """
        try:
            if workflow_id:
                step_ids = self._get_workflow_step_ids(workflow_id)
                if not step_ids:
                    return {
                        'error': f'No steps found for workflow {workflow_id}'
                    }
                
                # Get workflow execution metrics
                execution_metrics = {
                    'success': self.workflow_executions.labels(workflow_id=workflow_id, status='success').collect()[0].samples[0].value,
                    'error': self.workflow_executions.labels(workflow_id=workflow_id, status='error').collect()[0].samples[0].value,
                    'latency': {
                        status: self.workflow_execution_latency.labels(workflow_id=workflow_id, status=status).collect()[0].samples[0].value
                        for status in ['success', 'error']
                    },
                    'steps': {
                        step_id: {
                            'success': self.workflow_step_executions.labels(workflow_id=workflow_id, step_id=step_id, status='success').collect()[0].samples[0].value,
                            'error': self.workflow_step_executions.labels(workflow_id=workflow_id, step_id=step_id, status='error').collect()[0].samples[0].value,
                            'latency': {
                                status: self.workflow_step_latency.labels(workflow_id=workflow_id, step_id=step_id, status=status).collect()[0].samples[0].value
                                for status in ['success', 'error']
                            }
                        }
                        for step_id in step_ids
                    }
                }
                
                return {
                    'id': workflow_id,
                    'executions': execution_metrics,
                    'step_count': len(step_ids)
                }
            else:
                # Get aggregated metrics for all workflows
                return {
                    'executions': {
                        f"{workflow_id}:{status}": self.workflow_executions.labels(workflow_id=workflow_id, status=status).collect()[0].samples[0].value
                        for workflow_id, status in self.workflow_executions._metrics.keys()
                    },
                    'execution_latency': {
                        f"{workflow_id}:{status}": self.workflow_execution_latency.labels(workflow_id=workflow_id, status=status).collect()[0].samples[0].value
                        for workflow_id, status in self.workflow_execution_latency._metrics.keys()
                    }
                }
        except Exception as e:
            logger.error(f"Error retrieving workflow metrics: {e}")
            self.increment_error("workflow_metrics", str(e))
            return {
                'error': str(e)
            }

    def _get_workflow_step_ids(self, workflow_id: str) -> List[str]:
        """Get all step IDs for a workflow."""
        try:
            # In a real implementation, this should query the workflow definition store
            # For now, we'll use a mock implementation that returns step IDs based on workflow ID
            # In production, this should be replaced with actual workflow definition lookup
            if not workflow_id:
                return []
                
            # Mock implementation - in real code, this would query the database
            # Format: workflow_{id}_step_{number}
            return [f"workflow_{workflow_id}_step_{i}" for i in range(1, 6)]
        except Exception as e:
            logger.error(f"Failed to get step IDs for workflow {workflow_id}: {e}")
            self.increment_error("workflow", f"step_retrieval_{workflow_id}")
            return []

    def get_db_metrics(self) -> Dict[str, Any]:
        """Get database metrics."""
        try:
            return {
                'query_count': {
                    f"{query_type}:{table}:{operation}": self.db_query_count.labels(query_type=query_type, table=table, operation=operation).collect()[0].samples[0].value
                    for query_type, table, operation in self.db_query_count._metrics.keys()
                },
                'query_latency': {
                    f"{query_type}:{table}:{operation}": self.db_query_latency.labels(query_type=query_type, table=table, operation=operation).collect()[0].samples[0].value
                    for query_type, table, operation in self.db_query_latency._metrics.keys()
                },
                'query_errors': {
                    f"{query_type}:{table}:{operation}:{error_type}": self.db_query_errors.labels(query_type=query_type, table=table, operation=operation, error_type=error_type).collect()[0].samples[0].value
                    for query_type, table, operation, error_type in self.db_query_errors._metrics.keys()
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving database metrics: {e}")
            raise

    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache metrics."""
        try:
            total_hits = self.cache_hits._value.get()
            total_misses = self.cache_misses._value.get()
            total_operations = total_hits + total_misses
            
            return {
                'hits': total_hits,
                'misses': total_misses,
                'latency': {
                    operation: self.cache_latency.labels(operation=operation).collect()[0].samples[0].value
                    for operation in self.cache_latency._metrics.keys()
                },


                'hit_rate': total_hits / total_operations if total_operations > 0 else 0,
                'total_operations': total_operations
            }
        except Exception as e:
            logger.error(f"Error retrieving cache metrics: {e}")
            raise

    def get_request_metrics(self) -> Dict[str, Any]:
        """Get request metrics."""
        try:
            return {
                'count': {
                    f"{endpoint}:{method}:{status}:{user_agent}": self.request_count.labels(endpoint=endpoint, method=method, status=status, user_agent=user_agent).collect()[0].samples[0].value
                    for endpoint, method, status, user_agent in self.request_count._metrics.keys()
                },
                'latency': {
                    f"{endpoint}:{method}:{status}:{user_agent}": self.request_latency.labels(endpoint=endpoint, method=method, status=status, user_agent=user_agent).collect()[0].samples[0].value
                    for endpoint, method, status, user_agent in self.request_latency._metrics.keys()
                },
                'active': {
                    endpoint: self.active_requests.labels(endpoint=endpoint).collect()[0].samples[0].value
                    for endpoint in self.active_requests._metrics.keys()
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving request metrics: {e}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            'system': self.get_system_metrics(),
            'workflow': self.get_workflow_metrics(),
            'database': self.get_db_metrics(),
            'cache': self.get_cache_metrics(),
            'requests': self.get_request_metrics()
        }

if __name__ == "__main__":
    # Example usage
    monitor = PerformanceMonitor()
    
    # Example request monitoring
    with monitor.monitor_request("/api/workflow", "POST", "curl/7.64.1"):
        # Simulate request processing
        time.sleep(0.1)
    
    # Example database query monitoring
    with monitor.monitor_db_query("SELECT", "workflows", "read"):
        # Simulate database query
        time.sleep(0.05)
    
    # Example cache operation monitoring
    with monitor.monitor_cache_operation("get"):
        # Simulate cache operation
        time.sleep(0.001)
    
    # Example workflow execution monitoring
    with monitor.monitor_workflow_execution("workflow-123"):
        # Simulate workflow execution
        time.sleep(0.5)
    
    # Example workflow step monitoring
    with monitor.monitor_workflow_step("workflow-123", "step-456"):
        # Simulate step execution
        time.sleep(0.2)
    
    # Example error monitoring
    monitor.increment_error("DatabaseError", "db_connection")
    
    # Example authentication monitoring
    monitor.monitor_auth_attempt("success", "jwt")
    
    # Example rate limiting monitoring
    monitor.monitor_rate_limit("/api/workflow", "user-123", False)
    
    # Example health status update
    monitor.update_health_status("healthy")
    
    # Example metrics retrieval
    print("System Metrics:", monitor.get_system_metrics())
    print("Workflow Metrics:", monitor.get_workflow_metrics("workflow-123"))
    print("DB Metrics:", monitor.get_db_metrics())
    print("Cache Metrics:", monitor.get_cache_metrics())
    print("Request Metrics:", monitor.get_request_metrics())

# Create monitor instance
performance_monitor = PerformanceMonitor()
            hit: Whether the operation was a cache hit
            size: Cache size in bytes (optional)
        """
        if hit:
            self.cache_hits.inc()
        else:
            self.cache_misses.inc()
        
        if size is not None:
            self.cache_size.set(size)

    def monitor_workflow_execution(self, workflow_id: str, status: str, duration: float):
        """
        Record workflow execution metrics.
        
        Args:
            workflow_id: ID of the workflow
            status: Execution status
            return health
        except Exception as e:
            logger.error(f"Error calculating health status: {e}")
            self.increment_error("health_status", str(e))
            return {
                'status': 'error',
                'error': str(e)
            }

# Create monitor instance
performance_monitor = PerformanceMonitor()
