"""
Environment configuration for tests.
"""
import os
from pathlib import Path

# Set TESTING environment variable
def set_testing_env():
    """Set TESTING environment variable."""
    os.environ['TESTING'] = 'true'

# Set test environment variables
def set_test_env_vars():
    """Set test-specific environment variables."""
    os.environ['PYTHONPATH'] = str(Path(__file__).parent.parent.parent)
    os.environ['TEST_ENV'] = str(Path(__file__).parent.parent.parent / 'test_env')
    os.environ['TEST_DATA_DIR'] = str(Path(__file__).parent.parent / 'data')
    os.environ['TEST_REPORTS_DIR'] = str(Path(__file__).parent.parent / 'reports')

# Initialize environment
def init_test_env():
    """Initialize test environment."""
    set_testing_env()
    set_test_env_vars()

# Test configuration
TEST_CONFIG = {
    "RATE_LIMIT_MAX_REQUESTS": 100,
    "RATE_LIMIT_WINDOW": 60,
    "SECURITY_HEADERS": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    },
    "API_BASE_URL": "http://localhost:8000",
    "API_TIMEOUT": 30,
    "API_MAX_RETRIES": 3,
    "LOG_LEVEL": "INFO",
    "DATABASE_URL": "sqlite:///./test.db",
    "COVERAGE_DIR": str(Path(__file__).parent.parent / "reports" / "coverage"),
    "COVERAGE_MIN": 80.0,
    "PERFORMANCE_MAX_REQUESTS": 1000,
    "PERFORMANCE_WINDOW": 60,
    "PERFORMANCE_TARGET_RPS": 100.0
}

# Run initialization on import
init_test_env()
