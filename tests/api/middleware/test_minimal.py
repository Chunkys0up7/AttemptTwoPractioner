"""
Test file to verify module imports and basic functionality.
"""
import pytest
import sys
import os

# Add the project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from mcp.api.middleware.security import SecurityMiddleware
    print("Successfully imported SecurityMiddleware")
except ImportError as e:
    print(f"Import error: {e}")
    print("Current PYTHONPATH:")
    for path in sys.path:
        print(path)

def test_basic():
    """Basic test to verify pytest is working."""
    assert True

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2

if __name__ == "__main__":
    pytest.main()
