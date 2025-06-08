"""
Test environment setup and configuration.
"""
import pytest
import logging
from pathlib import Path
from tests.config.test_config import TestConfig, TestEnvironment
from tests.utils.test_utils import setup_test_logging

# Set up test logging
logger = setup_test_logging(level="DEBUG")

def test_environment_setup():
    """Test environment setup."""
    logger.info("Starting environment setup test")
    
    # Create test config
    config = TestConfig()
    assert isinstance(config, TestConfig)
    assert config.testing is True
    
    # Create test environment
    env = TestEnvironment(config)
    assert isinstance(env, TestEnvironment)
    
    # Check environment variables
    assert os.getenv("TESTING") == "true"
    assert os.getenv("DATABASE_URL") == config.database_url
    assert os.getenv("API_BASE_URL") == config.api_base_url
    
    # Check directory creation
    assert config.test_env_dir.exists()
    assert config.test_data_dir.exists()
    assert config.test_reports_dir.exists()
    
    logger.info("Environment setup test successful")

def test_logging_setup():
    """Test logging setup."""
    logger.info("Starting logging setup test")
    
    # Test different log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Check log file creation
    log_file = Path(os.getenv("TEST_LOG_FILE", "tests/reports/logs/test.log"))
    assert log_file.exists()
    assert log_file.stat().st_size > 0  # Check if file has content
    
    logger.info("Logging setup test successful")

def test_database_setup():
    """Test database setup."""
    logger.info("Starting database setup test")
    
    config = TestConfig()
    env = TestEnvironment(config)
    
    # Get database session
    SessionLocal = env.setup_test_database()
    session = SessionLocal()
    
    # Test basic database operations
    try:
        # This is a basic test - in real tests you would add actual database operations
        assert session is not None
        logger.info("Database session created successfully")
    finally:
        # Always close the session
        session.close()
    
    logger.info("Database setup test successful")

def test_api_setup():
    """Test API setup."""
    logger.info("Starting API setup test")
    
    config = TestConfig()
    env = TestEnvironment(config)
    
    # Get API client
    api_client = env.setup_test_api()
    
    # Test basic API connection
    try:
        # This is a basic test - in real tests you would add actual API calls
        assert api_client is not None
        logger.info("API client created successfully")
    finally:
        # Always close the client
        api_client.close()
    
    logger.info("API setup test successful")

def test_security_setup():
    """Test security setup."""
    logger.info("Starting security setup test")
    
    config = TestConfig()
    env = TestEnvironment(config)
    
    # Get security context
    security = env.setup_test_security()
    
    # Test token creation
    test_token = security["create_token"]({"sub": "testuser"})
    assert isinstance(test_token, str)
    assert len(test_token) > 0
    
    logger.info("Security setup test successful")
