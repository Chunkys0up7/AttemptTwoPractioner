"""
Minimal test file in root directory.
"""
import pytest

def test_basic():
    """Basic test to verify pytest is working."""
    assert True

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2

if __name__ == "__main__":
    pytest.main()
