"""
Minimal test file to verify basic test execution and environment setup.
"""
import pytest
import os
from mcp.core.config import settings
from mcp.core.monitoring import monitor

@pytest.mark.unit
@pytest.mark.basic
def test_environment_setup():
    """Test that environment variables are properly set."""
    assert os.getenv('TESTING') == 'true'
    assert settings.TESTING is True
    
@pytest.mark.unit
@pytest.mark.basic
def test_monitor_setup():
    """Test that monitor is properly initialized in test mode."""
    assert hasattr(monitor, 'get_metrics')
    assert hasattr(monitor, 'check_thresholds')
    assert hasattr(monitor, 'reset_metrics')
    
@pytest.mark.unit
@pytest.mark.basic
def test_settings():
    """Test that settings are properly loaded."""
    assert settings.API_V1_STR == '/api/v1'
    assert settings.DOCS_URL is None
    assert settings.REDIS_URL is None
    
@pytest.mark.unit
@pytest.mark.basic
def test_addition():
    """Test basic arithmetic."""
    assert 1 + 1 == 2
    assert 2 + 2 == 4
    
@pytest.mark.unit
@pytest.mark.basic
def test_string_operations():
    """Test basic string operations."""
    assert len('test') == 4
    assert 'test'.upper() == 'TEST'
    assert 'test'.lower() == 'test'
    assert 'test'.startswith('t')
    assert 'test'.endswith('t')
    assert 1 + 1 == 2
