"""
Test runner script that properly sets up the Python environment and runs all tests.
"""
import os
import sys
import pytest
import logging
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root and backend directories to PYTHONPATH
def setup_environment():
    """Set up Python environment for testing."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_dir = os.path.join(project_root, 'mcp_project_backend')
    
    # Ensure both directories are in PYTHONPATH
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    logger.info("\nPYTHONPATH:")
    for path in sys.path:
        logger.info(path)
    
    logger.info("\nCurrent working directory: %s", os.getcwd())

def verify_imports():
    """Verify that key modules can be imported."""
    try:
        # Import using importlib to ensure proper module loading
        security_module = importlib.import_module('mcp.api.middleware.security')
        config_module = importlib.import_module('mcp.core.config')
        monitoring_module = importlib.import_module('mcp.core.monitoring')
        
        logger.info("\nSuccessfully imported key modules")
        logger.info("SecurityMiddleware location: %s", security_module.SecurityMiddleware.__module__)
        logger.info("Settings location: %s", config_module.settings.__module__)
        logger.info("Monitor location: %s", monitoring_module.monitor.__module__)
        return True
    except ImportError as e:
        logger.error("\nImport error: %s", e)
        logger.info("\nAvailable modules:")
        for module in sorted(sys.modules.keys()):
            logger.info(module)
        return False

def run_tests():
    """Run the test suite."""
    # Disable problematic pytest plugins
    test_args = [
        "tests",  # Run all tests in tests directory
        "-v",     # Verbose output
        "-s",     # Don't capture stdout/stderr
        "--tb=short",  # Show short tracebacks
        "--import-mode=importlib",  # Use importlib for imports
        "-p", "no:importlib",  # Disable importlib plugin
        "-p", "no:pytester",   # Disable pytester plugin
        "-p", "no:cacheprovider",  # Disable cache plugin
        "--no-header",  # Disable header output
        "--no-summary",  # Disable summary output
        "--tb=short"  # Show short tracebacks
    ]
    
    logger.info("\nRunning tests with args: %s", test_args)
    
    # Run pytest with error handling
    try:
        pytest.main(test_args)
    except Exception as e:
        logger.error("Test execution failed: %s", e)
        sys.exit(1)

def main():
    """Main entry point."""
    logger.info("Starting test runner...")
    
    # Setup environment
    setup_environment()
    
    # Verify imports
    if not verify_imports():
        logger.error("Failed to import required modules")
        sys.exit(1)
    
    # Run tests
    run_tests()

if __name__ == "__main__":
    main()
