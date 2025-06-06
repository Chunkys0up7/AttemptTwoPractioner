# Error Handling & Logging

This document describes the error handling and logging system implemented in the MCP Backend.

## Overview

The error handling and logging system provides:

1. Custom exception classes for different error types
2. Consistent error response format
3. Request/response logging middleware
4. Utility functions for logging

## Error Handling

### Custom Exceptions

The system defines several custom exception classes in `mcp/core/errors.py`:

1. `MCPError`: Base exception class for all MCP errors
2. `ResourceNotFoundError`: For 404 Not Found errors
3. `ValidationError`: For 422 Unprocessable Entity errors
4. `AuthenticationError`: For 401 Unauthorized errors
5. `AuthorizationError`: For 403 Forbidden errors
6. `WorkflowError`: For workflow-specific errors

### Error Response Format

All errors are returned in a consistent JSON format:

```json
{
  "message": "Error message",
  "details": {
    "field": "Additional error details"
  }
}
```

### Usage Example

```python
from mcp.core.errors import ResourceNotFoundError

def get_resource(resource_id: str):
    resource = db.query(Resource).filter_by(id=resource_id).first()
    if not resource:
        raise ResourceNotFoundError("Resource", resource_id)
    return resource
```

## Logging

### Logging Middleware

The `LoggingMiddleware` in `mcp/core/logging.py` automatically logs:

1. Request details (method, path, client IP)
2. Response status and processing time
3. Errors with full stack traces

### Logging Configuration

Logging is configured to output to both:

- Console (stdout)
- File (`mcp.log`)

Log format:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Logging Utility Functions

The system provides utility functions for different log levels:

```python
from mcp.core.logging import log_error, log_info, log_warning, log_debug

# Log an error with context
log_error(error, {"context": "additional info"})

# Log informational message
log_info("Operation completed", {"operation_id": "123"})

# Log warning
log_warning("Resource running low", {"resource": "memory"})

# Log debug information
log_debug("Processing step", {"step": "validation"})
```

## Integration with FastAPI

The error handling and logging system is integrated with FastAPI through:

1. Custom exception handlers
2. Middleware for request/response logging
3. Dependency injection for logging context

### Example FastAPI Integration

```python
from fastapi import FastAPI
from mcp.core.logging import LoggingMiddleware
from mcp.core.errors import handle_mcp_error

app = FastAPI()
app.add_middleware(LoggingMiddleware)

@app.exception_handler(MCPError)
async def mcp_error_handler(request, exc):
    return handle_mcp_error(exc)
```

## Testing

The error handling and logging system is tested in `tests/core/test_error_handling.py`. The test suite includes:

1. Tests for each custom exception type
2. Tests for error response format
3. Tests for logging middleware
4. Tests for logging utility functions

## Best Practices

1. **Error Handling**

   - Use appropriate custom exceptions
   - Include relevant details in error messages
   - Handle errors at the appropriate level

2. **Logging**

   - Log at appropriate levels (ERROR, INFO, WARNING, DEBUG)
   - Include context in log messages
   - Use structured logging for better analysis

3. **Security**
   - Don't log sensitive information
   - Sanitize error messages
   - Use appropriate log levels for security events

## Future Enhancements

1. **Error Handling**

   - Add error codes for better client handling
   - Implement error translation
   - Add error aggregation

2. **Logging**
   - Add log rotation
   - Implement log aggregation
   - Add performance metrics
   - Add request tracing
