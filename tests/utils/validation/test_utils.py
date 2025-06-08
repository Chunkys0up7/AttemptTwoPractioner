"""
Test utility functions and helpers.
"""
import os
import json
import pytest
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Callable
from datetime import datetime
import time
import logging
from tests.config.env_config import TEST_CONFIG
from mcp.core.config import settings
from mcp.core.logging import setup_logging
from mcp.core.monitoring import monitor
from mcp.core.database import get_db_session

# Test data directory
TEST_DATA_DIR = Path(os.getenv('TEST_DATA_DIR', 'tests/data'))

# Test fixtures
# Test data directory
TEST_DATA_DIR = Path(os.getenv('TEST_DATA_DIR', 'tests/data'))

def load_test_data(filename: str, data_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load test data from JSON file.
    
    Args:
        filename: Name of the test data file
        data_dir: Optional custom data directory path
    
    Returns:
        Dictionary containing test data
    """
    if data_dir is None:
        data_dir = test_config.data_dir
    
    try:
        with open(data_dir / filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pytest.fail(f"Test data file not found: {filename}")
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON in test data file {filename}: {str(e)}")

def create_test_user(
    username: str = "testuser",
    password: str = "testpassword",
    email: str = "test@example.com",
    **kwargs
) -> Dict[str, Any]:
    """Create a test user with customizable attributes.
    
    Args:
        username: Username for the test user
        password: Password for the test user
        email: Email address for the test user
        **kwargs: Additional user attributes
    
    Returns:
        Dictionary containing user data
    """
    user = {
        "username": username,
        "password": password,
        "email": email,
        **kwargs
    }
    return user

def create_test_workflow(
    name: str = "Test Workflow",
    description: str = "Test workflow description",
    steps: List[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a test workflow with customizable attributes.
    
    Args:
        name: Name of the workflow
        description: Description of the workflow
        steps: List of workflow steps
        **kwargs: Additional workflow attributes
    
    Returns:
        Dictionary containing workflow data
    """
    if steps is None:
        steps = []
    
    workflow = {
        "name": name,
        "description": description,
        "steps": steps,
        **kwargs
    }
    return workflow

# Test data helpers
def load_test_data(filename: str) -> Dict[str, Any]:
    """Load test data from JSON file."""
    with open(TEST_DATA_DIR / filename, 'r') as f:
        return json.load(f)

# Test cleanup helpers
def cleanup_test_data():
    """Clean up test data."""
    # Add cleanup logic here
    pass

# Test environment helpers
def setup_test_environment():
    """Set up test environment."""
    os.environ['TESTING'] = 'true'
    os.environ['PYTHONPATH'] = str(Path(__file__).parent.parent.parent)
    os.environ['TEST_ENV'] = str(Path(__file__).parent.parent.parent / 'test_env')
    os.environ['TEST_DATA_DIR'] = str(TEST_DATA_DIR)
    os.environ['TEST_REPORTS_DIR'] = str(Path(__file__).parent.parent / 'reports')

# Test validation helpers
def validate_workflow(
    workflow: Dict[str, Any],
    required_fields: List[str] = None
) -> bool:
    """Validate workflow structure.
    
    Args:
        workflow: Workflow dictionary to validate
        required_fields: List of required field names
    
    Returns:
        Boolean indicating if workflow is valid
    """
    if required_fields is None:
        required_fields = ["name", "description", "steps"]
    
    for field in required_fields:
        if field not in workflow:
            pytest.fail(f"Missing required field in workflow: {field}")
    
    return True

# Test performance helpers
def measure_performance(
    func: Callable,
    *args,
    **kwargs
) -> float:
    """Measure function execution time.
    
    Args:
        func: Function to measure
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
    
    Returns:
        Execution time in seconds
    """
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        monitor.performance(
            name=func.__name__,
            duration=duration,
            timestamp=datetime.now()
        )
        return duration
    except Exception as e:
        monitor.error(
            name=func.__name__,
            error=str(e),
            timestamp=datetime.now()
        )
        raise e

# Test error handling helpers
def assert_error_type(
    error: Exception,
    expected_type: str,
    message: Optional[str] = None
) -> None:
    """Assert error type and optionally check error message.
    
    Args:
        error: Exception instance
        expected_type: Expected error type
        message: Optional message to check in error
    """
    assert hasattr(error, "type"), "Error object must have a type attribute"
    assert error.type == expected_type, f"Expected error type {expected_type}, got {error.type}"
    
    if message and hasattr(error, "message"):
        assert message in error.message, f"Expected '{message}' in error message, got '{error.message}'"

# Test logging helpers
def setup_test_logging(
    level: str = "INFO",
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """Set up test logging with proper configuration.
    
    Args:
        level: Logging level (INFO, DEBUG, etc.)
        format: Log message format
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    
    # Create file handler
    log_file = test_config.log_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(format))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(format))
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Test database helpers
def setup_test_database():
    """Set up test database."""
    # Add test database setup logic here
    pass

# Test cleanup helpers
def cleanup_test_database():
    """Clean up test database."""
    # Add test database cleanup logic here
    pass

# Test monitoring helpers
def setup_test_monitoring():
    """Set up test monitoring."""
    # Add test monitoring setup logic here
    pass

# Test security helpers
def setup_test_security():
    """Set up test security."""
    # Add test security setup logic here
    pass
