"""
Basic test to verify package imports.
"""
import pytest

# Add project root to PYTHONPATH
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Test imports
def test_import_mcp():
    """Test importing the mcp package."""
    import mcp
    assert hasattr(mcp, '__version__')
    assert hasattr(mcp, 'settings')
    assert hasattr(mcp, 'monitor')
    assert hasattr(mcp, 'SecurityMiddleware')

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
