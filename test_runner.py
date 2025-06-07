"""
Test runner script that properly sets up the Python environment.
"""
import os
import sys
import pytest

# Add the project root and backend directories to PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, 'mcp_project_backend')

# Ensure both directories are in PYTHONPATH
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Print PYTHONPATH for debugging
print("\nPYTHONPATH:")
for path in sys.path:
    print(path)

# Print current working directory
print("\nCurrent working directory:", os.getcwd())

# Import the security middleware module directly
try:
    from mcp.api.middleware.security import SecurityMiddleware
    print("\nSuccessfully imported SecurityMiddleware")
    print("SecurityMiddleware location:", SecurityMiddleware.__module__)
except ImportError as e:
    print(f"\nImport error: {e}")
    print("\nAvailable modules:")
    print("\n".join(sys.modules.keys()))
    sys.exit(1)

if __name__ == "__main__":
    # Run tests with verbose output and show full traceback
    print("\nRunning tests...")
    pytest.main(["tests/api/middleware/test_security_middleware.py", "-v", "-s", "--tb=short", "--import-mode=importlib"])
