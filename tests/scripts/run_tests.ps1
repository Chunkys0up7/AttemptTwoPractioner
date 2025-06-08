"""
Test runner script that properly sets up the Python environment and runs all tests.
"""
import os
import sys
import logging
import pytest
import importlib
from pathlib import Path
from tests.config.env_config import TEST_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """Set up Python environment for testing."""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "mcp_project_backend"
    
    # Ensure both directories are in PYTHONPATH
    if backend_dir not in sys.path:
        sys.path.insert(0, str(backend_dir))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    logger.info("\nPYTHONPATH:")
    for path in sys.path:
        logger.info(path)
    
    logger.info(f"\nCurrent working directory: {os.getcwd()}")

def verify_imports() -> bool:
    """Verify that key modules can be imported."""
    try:
        # Import using importlib to ensure proper module loading
        security_module = importlib.import_module('mcp.api.middleware.security')
        config_module = importlib.import_module('mcp.core.config')
        monitoring_module = importlib.import_module('mcp.core.monitoring')
        
        logger.info("\nSuccessfully imported key modules")
        logger.info(f"SecurityMiddleware location: {security_module.SecurityMiddleware.__module__}")
        logger.info(f"Settings location: {config_module.settings.__module__}")
        logger.info(f"Monitor location: {monitoring_module.monitor.__module__}")
        return True
    except ImportError as e:
        logger.error(f"\nImport error: {e}")
        logger.info("\nAvailable modules:")
        for module in sorted(sys.modules.keys()):
            logger.info(module)
        return False

def run_tests() -> None:
    """Run the test suite."""
    logger.info("\nStarting test suite...")
    
    # Set up environment
    setup_environment()
    
    # Verify imports
    if not verify_imports():
        logger.error("Import verification failed")
        sys.exit(1)
    
    # Run pytest with coverage
    pytest_args = [
        "-v",
        "--tb=short",
        "--import-mode=importlib",
        "--cov=mcp",
        "--cov-report=html:tests/reports/coverage",
        "--cov-report=term-missing",
        "--junit-xml=tests/reports/junit.xml"
    ]
    
    # Add test directories
    pytest_args.extend([
        "tests/api/",
        "tests/e2e/",
        "tests/performance/",
        "tests/accessibility/"
    ])
    
    # Run pytest
    result = pytest.main(pytest_args)
    
    if result == 0:
        logger.info("\nAll tests passed!")
    else:
        logger.error(f"\nTests failed with exit code {result}")
        sys.exit(result)

if __name__ == "__main__":
    run_tests()
