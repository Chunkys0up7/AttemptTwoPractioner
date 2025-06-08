"""
Script to run tests with proper module imports.
"""
import sys
import os
import pytest

# Add the project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    pytest.main(["tests/api/middleware/test_security_middleware.py", "-v"])
