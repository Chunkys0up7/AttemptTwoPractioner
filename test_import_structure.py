"""
Script to analyze module import structure and paths.
"""
import sys
import os
import importlib

# Print current PYTHONPATH
print("\nCurrent PYTHONPATH:")
for path in sys.path:
    print(path)

# Try importing the module and print its file location
try:
    security_module = importlib.import_module('mcp.api.middleware.security')
    print(f"\nSecurity module location: {security_module.__file__}")
    print(f"Security module package: {security_module.__package__}")
except ImportError as e:
    print(f"\nImport error: {e}")

# List all files in the mcp directory
mcp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mcp')
print(f"\nFiles in mcp directory ({mcp_dir}):")
for root, dirs, files in os.walk(mcp_dir):
    for file in files:
        print(os.path.join(root, file))

if __name__ == "__main__":
    print("Running test_import_structure.py")
