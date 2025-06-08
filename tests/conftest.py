"""
Global pytest configuration and fixtures.
"""
import pytest
import os
from pathlib import Path
import sys
from mcp.core.config import settings

# Set up test environment
os.environ['TESTING'] = 'true'

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(autouse=True)
def test_environment():
    """Test environment setup fixture."""
    # Import test environment configuration
    from tests.test_environment import settings, engine, SessionLocal
    
    # Override database session dependency
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Import app after test environment is set up
    from mcp.api.main import app
    
    # Override the database session dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Return settings for test configuration
    return settings

@pytest.fixture
def test_client():
    """Test client fixture for API testing."""
    from mcp.api.main import app
    return TestClient(app)

@pytest.fixture
def test_session(test_environment):
    """Test database session fixture."""
    from tests.test_environment import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_db(test_environment):
    """Test database fixture."""
    from tests.test_environment import engine
    from mcp.db.base import Base
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
