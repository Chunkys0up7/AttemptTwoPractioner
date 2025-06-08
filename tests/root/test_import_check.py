"""
Test file to verify module imports and print PYTHONPATH.
"""
import sys
import os

# Print current PYTHONPATH
print("Current PYTHONPATH:")
for path in sys.path:
    print(path)

# Try importing the module
try:
    from mcp.api.middleware.security import SecurityMiddleware
    print("\nSuccessfully imported SecurityMiddleware")
    print("\nSecurityMiddleware attributes:")
    print(dir(SecurityMiddleware))
except ImportError as e:
    print(f"\nImport error: {e}")

if __name__ == "__main__":
    print("Running test_import_check.py")
