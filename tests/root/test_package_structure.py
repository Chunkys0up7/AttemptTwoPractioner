"""
Script to verify package structure and imports.
"""
import os
import sys
import importlib

# Add project root to PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("\nProject Root:", project_root)
print("\nPYTHONPATH:")
for path in sys.path:
    print(path)

# Try importing the package
try:
    mcp = importlib.import_module('mcp')
    print("\nSuccessfully imported mcp package")
    print("Package location:", mcp.__file__)
    print("Package contents:", dir(mcp))
except ImportError as e:
    print(f"\nImport error: {e}")

# List contents of mcp directory
mcp_dir = os.path.join(project_root, 'mcp_project_backend', 'mcp')
print(f"\nContents of {mcp_dir}:")
for item in os.listdir(mcp_dir):
    print(item)

if __name__ == "__main__":
    print("Running test_package_structure.py")
