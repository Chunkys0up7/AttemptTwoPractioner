# Performance Monitoring

This document describes the performance monitoring system implemented in the MCP Backend.

## Overview

The performance monitoring system provides:

1. HTTP request monitoring
2. Database operation monitoring
3. Workflow step monitoring
4. Prometheus metrics integration
5. Metrics endpoints for monitoring

## Components

### 1. Performance Monitoring Middleware

The `PerformanceMonitoringMiddleware` in `mcp/core/monitoring.py` automatically tracks:

- Request counts
- Request latency
- Response status codes

### 2. Database Operation Monitoring

The `monitor_db_operation` decorator tracks:

- Operation counts
- Operation latency
- Success/failure rates

```python
from mcp.core.monitoring import monitor_db_operation

@monitor_db_operation("select", "users")
async def get_user(user_id: str):
    # Database operation
    return user
```

### 3. Workflow Step Monitoring

The `monitor_workflow_step` decorator tracks:

- Step execution counts
- Step latency
- Success/failure rates
- Active workflow count

```python
from mcp.core.monitoring import monitor_workflow_step

@monitor_workflow_step("workflow_1", "step_1")
async def execute_step():
    # Workflow step execution
    return result
```

## Metrics

### Prometheus Metrics

The system exposes the following Prometheus metrics:

1. **HTTP Metrics**
   - `mcp_http_requests_total`: Total HTTP requests
   - `mcp_http_request_duration_seconds`: Request latency

2. **Database Metrics**
   - `mcp_db_operations_total`: Total database operations
   - `mcp_db_operation_duration_seconds`: Operation latency

3. **Workflow Metrics**
   - `mcp_workflow_steps_total`: Total workflow steps
   - `mcp_workflow_step_duration_seconds`: Step latency
   - `mcp_active_workflows`: Active workflow count

### Metrics Endpoints

The system provides two endpoints for accessing metrics:

1. `/metrics`: Prometheus format metrics
2. `/metrics/summary`: JSON summary of current metrics

## Integration

### FastAPI Integration

```python
from fastapi import FastAPI
from mcp.core.monitoring import PerformanceMonitoringMiddleware

app = FastAPI()
app.add_middleware(PerformanceMonitoringMiddleware)
```

### Prometheus Integration

1. Configure Prometheus to scrape the `/metrics` endpoint
2. Set up appropriate scrape intervals
3. Configure alerting rules based on metrics

## Usage Examples

### Monitoring Database Operations

```python
from mcp.core.monitoring import monitor_db_operation

class UserService:
    @monitor_db_operation("select", "users")
    async def get_user(self, user_id: str):
        return await self.db.query(User).filter_by(id=user_id).first()
    
    @monitor_db_operation("insert", "users")
    async def create_user(self, user_data: dict):
        user = User(**user_data)
        await self.db.add(user)
        await self.db.commit()
        return user
```

### Monitoring Workflow Steps

```python
from mcp.core.monitoring import monitor_workflow_step

class WorkflowEngine:
    @monitor_workflow_step("data_processing", "validation")
    async def validate_data(self, data: dict):
        # Validation logic
        return validation_result
    
    @monitor_workflow_step("data_processing", "transformation")
    async def transform_data(self, data: dict):
        # Transformation logic
        return transformed_data
```

## Testing

The performance monitoring system is tested in `tests/core/test_performance_monitoring.py`. The test suite includes:

1. Tests for HTTP request monitoring
2. Tests for database operation monitoring
3. Tests for workflow step monitoring
4. Tests for metrics endpoints

## Best Practices

1. **Monitoring**
   - Monitor all critical operations
   - Set appropriate alert thresholds
   - Use meaningful metric labels

2. **Performance**
   - Keep monitoring overhead minimal
   - Use appropriate sampling rates
   - Monitor resource usage

3. **Security**
   - Secure metrics endpoints
   - Sanitize metric labels
   - Control access to metrics

## Future Enhancements

1. **Metrics**
   - Add custom metrics
   - Implement metric aggregation
   - Add metric retention policies

2. **Monitoring**
   - Add distributed tracing
   - Implement APM integration
   - Add performance profiling

3. **Visualization**
   - Add Grafana dashboards
   - Implement metric visualization
   - Add performance reports

## New Endpoints (2024-06)

- `GET /api/v1/metrics/report`: Returns a JSON summary of key metrics and current alerts.
- `POST /api/v1/metrics/reset`: Resets all in-memory performance metrics (admin only).

## Alerting

The system implements threshold-based alerting for key performance metrics:

### Threshold Settings

1. **System Performance**
   - **Request Latency**: >1.0s (configurable via `settings.REQUEST_LATENCY_THRESHOLD`)
   - **Error Rate**: >5% (configurable via `settings.ERROR_RATE_THRESHOLD`)
   - **Memory Usage**: >80% (configurable via `settings.MEMORY_THRESHOLD`)
   - **CPU Usage**: >80% (configurable via `settings.CPU_THRESHOLD`)

2. **Resource Utilization**
   - **Cache Hit Ratio**: <80% (configurable via `settings.CACHE_HIT_RATIO_THRESHOLD`)
   - **Database Connection Pool**: >90% utilization (configurable via `settings.DB_POOL_THRESHOLD`)

### Alert Types

1. **Performance Alerts**
   - High request latency
   - High error rate
   - High memory usage
   - High CPU usage

2. **Resource Alerts**
   - Low cache hit ratio
   - High database connection pool utilization
   - High system load

### Alert Handling

- Alerts are generated when thresholds are exceeded
- Alerts include:
  - Alert type
  - Current value
  - Threshold value
  - Timestamp
  - Affected components
- Alerts are logged and exposed via API endpoints

## Dashboard Endpoint

The `/api/v1/metrics/dashboard` endpoint provides a comprehensive overview of system performance and health:

### Available Metrics

1. **System Health**
   - Uptime
   - Request count
   - Error count
   - Response times
   - Active workflows

2. **Resource Usage**
   - Memory usage
   - CPU usage
   - Cache metrics
   - Database metrics

3. **Workflow Performance**
   - Active workflows
   - Workflow completion rate
   - Workflow execution time
   - Workflow error rate

4. **Alerts**
   - Active alerts
   - Alert history
   - Alert severity levels
   - Affected components

### Response Format

```json
{
  "system": {
    "uptime": "12h 34m",
    "requests": {
      "total": 12345,
      "errors": 12,
      "average_latency": "123ms"
    },
    "resources": {
      "memory": "65%",
      "cpu": "45%",
      "cache_hit_ratio": "85%"
    }
  },
  "alerts": {
    "active": [
      {
        "type": "HIGH_CPU_USAGE",
        "current_value": "85%",
        "threshold": "80%",
        "timestamp": "2025-06-07T15:57:04-04:00"
      }
    ],
    "history": [...]
  }
}
```

## Retention/Cleanup

- Metrics are reset automatically every 24 hours (in-memory cleanup).
- Metrics can also be reset manually via the `/metrics/reset` endpoint.

## Usage Notes

- Use `/metrics/dashboard` for admin dashboards or monitoring UIs.
- Use `/metrics/report` for detailed metrics and alert review.
- Alerts are in-memory only and reset every 24 hours or via the reset endpoint. 