"""
Test file to verify module imports.
"""
import sys
import os

# Add the project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.api.middleware.security import SecurityMiddleware
    print("Successfully imported SecurityMiddleware")
except ImportError as e:
    print(f"Import error: {e}")
    print("Current PYTHONPATH:")
    for path in sys.path:
        print(path)

if __name__ == "__main__":
    print("Running test_import.py")
