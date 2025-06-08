"""
Basic test to verify test environment setup.
"""
import os

def test_environment_setup(test_config):
    """Test that the test environment is properly set up."""
    assert os.environ.get('TESTING') == 'true'
    assert test_config['test_env'] == 'true'
    print("Basic test environment setup verified")
