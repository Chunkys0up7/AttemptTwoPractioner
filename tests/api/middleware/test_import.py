"""
Test file to verify module imports.
"""
import pytest
from mcp.api.middleware.security import SecurityMiddleware
from mcp.core.config import settings
from mcp.core.monitoring import monitor

def test_imports():
    """Test that imports work correctly."""
    assert SecurityMiddleware is not None
    assert settings is not None
    assert monitor is not None

if __name__ == "__main__":
    pytest.main()
