"""
Test assertion utilities and helpers.
"""
import pytest
from typing import Dict, Any, List, Optional
from fastapi.testclient import TestClient
import json
import time

def assert_response_ok(
    response,
    status_code: int = 200,
    content_type: str = "application/json"
) -> None:
    """Assert response status and headers."""
    assert response.status_code == status_code
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"].startswith(content_type)

def assert_security_headers(response) -> None:
    """Assert security headers are present."""
    headers = response.headers
    assert "Strict-Transport-Security" in headers
    assert "X-Content-Type-Options" in headers
    assert "X-Frame-Options" in headers
    assert "X-XSS-Protection" in headers
    assert "Content-Security-Policy" in headers

def assert_rate_limit_headers(response, remaining: Optional[int] = None) -> None:
    """Assert rate limit headers are present."""
    headers = response.headers
    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers
    assert "X-RateLimit-Reset" in headers
    
    if remaining is not None:
        assert int(headers["X-RateLimit-Remaining"]) == remaining

def assert_pagination(response, total: int, page: int, size: int) -> None:
    """Assert pagination response structure."""
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()
    
    assert response.json()["total"] == total
    assert response.json()["page"] == page
    assert response.json()["size"] == size
    assert len(response.json()["items"]) <= size

def assert_workflow_structure(workflow: Dict[str, Any]) -> None:
    """Assert workflow has correct structure."""
    required_fields = ["name", "description", "components", "connections"]
    for field in required_fields:
        assert field in workflow
    
    assert isinstance(workflow["name"], str)
    assert isinstance(workflow["description"], str)
    assert isinstance(workflow["components"], list)
    assert isinstance(workflow["connections"], list)

def assert_component_structure(component: Dict[str, Any]) -> None:
    """Assert component has correct structure."""
    required_fields = ["type", "name", "properties"]
    for field in required_fields:
        assert field in component
    
    assert isinstance(component["type"], str)
    assert isinstance(component["name"], str)
    assert isinstance(component["properties"], dict)

def assert_connection_structure(connection: Dict[str, Any]) -> None:
    """Assert connection has correct structure."""
    required_fields = ["source", "target"]
    for field in required_fields:
        assert field in connection
    
    assert isinstance(connection["source"], str)
    assert isinstance(connection["target"], str)

def assert_error_response(
    response,
    status_code: int,
    error_type: str,
    message: str
) -> None:
    """Assert error response structure."""
    assert response.status_code == status_code
    error_data = response.json()
    assert "error" in error_data
    assert "type" in error_data["error"]
    assert "message" in error_data["error"]
    assert error_data["error"]["type"] == error_type
    assert error_data["error"]["message"] == message

def assert_performance_metrics(
    response,
    max_latency_ms: float = 100.0
) -> None:
    """Assert performance metrics."""
    latency = response.elapsed.total_seconds() * 1000
    assert latency <= max_latency_ms, f"Response took {latency:.2f}ms > {max_latency_ms}ms"

def assert_cache_headers(response, cache_control: str = "no-cache") -> None:
    """Assert cache headers are present."""
    headers = response.headers
    assert "Cache-Control" in headers
    assert headers["Cache-Control"] == cache_control
    assert "ETag" in headers
