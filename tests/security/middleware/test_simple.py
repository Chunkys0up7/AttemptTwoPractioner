"""
Simple test file to help identify import issues.
"""
import pytest

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2

def test_string():
    """Test string concatenation."""
    assert "hello" + "world" == "helloworld"

def test_list():
    """Test list operations."""
    lst = [1, 2, 3]
    assert len(lst) == 3
    assert 3 in lst

if __name__ == "__main__":
    pytest.main()
