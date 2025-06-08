import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from mcp.core.errors import (
    MCPError,
    ResourceNotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    WorkflowError,
    handle_mcp_error
)
from mcp.core.logging import LoggingMiddleware, log_error, log_info, log_warning, log_debug

# Test app for middleware testing
app = FastAPI()
app.add_middleware(LoggingMiddleware)

@app.get("/test-error")
async def test_error():
    raise ResourceNotFoundError("test_resource", "123")

@app.get("/test-success")
async def test_success():
    return {"message": "success"}

client = TestClient(app)

def test_resource_not_found_error():
    """Test ResourceNotFoundError creation and handling."""
    error = ResourceNotFoundError("test_resource", "123")
    assert error.message == "test_resource with id 123 not found"
    assert error.status_code == 404
    
    http_exception = handle_mcp_error(error)
    assert http_exception.status_code == 404
    assert http_exception.detail["message"] == "test_resource with id 123 not found"

def test_validation_error():
    """Test ValidationError creation and handling."""
    error = ValidationError("Invalid input", {"field": "value"})
    assert error.message == "Invalid input"
    assert error.status_code == 422
    assert error.details == {"field": "value"}
    
    http_exception = handle_mcp_error(error)
    assert http_exception.status_code == 422
    assert http_exception.detail["message"] == "Invalid input"
    assert http_exception.detail["details"] == {"field": "value"}

def test_authentication_error():
    """Test AuthenticationError creation and handling."""
    error = AuthenticationError("Invalid credentials")
    assert error.message == "Invalid credentials"
    assert error.status_code == 401
    
    http_exception = handle_mcp_error(error)
    assert http_exception.status_code == 401
    assert http_exception.detail["message"] == "Invalid credentials"

def test_authorization_error():
    """Test AuthorizationError creation and handling."""
    error = AuthorizationError("Insufficient permissions")
    assert error.message == "Insufficient permissions"
    assert error.status_code == 403
    
    http_exception = handle_mcp_error(error)
    assert http_exception.status_code == 403
    assert http_exception.detail["message"] == "Insufficient permissions"

def test_workflow_error():
    """Test WorkflowError creation and handling."""
    error = WorkflowError("Workflow execution failed", {"step": "step1"})
    assert error.message == "Workflow execution failed"
    assert error.status_code == 400
    assert error.details == {"step": "step1"}
    
    http_exception = handle_mcp_error(error)
    assert http_exception.status_code == 400
    assert http_exception.detail["message"] == "Workflow execution failed"
    assert http_exception.detail["details"] == {"step": "step1"}

def test_logging_middleware_error():
    """Test LoggingMiddleware error handling."""
    response = client.get("/test-error")
    assert response.status_code == 404
    assert response.json()["message"] == "test_resource with id 123 not found"

def test_logging_middleware_success():
    """Test LoggingMiddleware success handling."""
    response = client.get("/test-success")
    assert response.status_code == 200
    assert response.json()["message"] == "success"

def test_logging_functions(caplog):
    """Test logging utility functions."""
    # Test error logging
    error = Exception("Test error")
    log_error(error, {"context": "test"})
    assert "Test error" in caplog.text
    assert "context" in caplog.text
    
    # Test info logging
    log_info("Test info", {"context": "test"})
    assert "Test info" in caplog.text
    
    # Test warning logging
    log_warning("Test warning", {"context": "test"})
    assert "Test warning" in caplog.text
    
    # Test debug logging
    log_debug("Test debug", {"context": "test"})
    assert "Test debug" in caplog.text 