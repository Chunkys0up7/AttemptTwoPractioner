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