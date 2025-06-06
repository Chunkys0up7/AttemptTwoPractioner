"""
Global test fixtures for Pytest.
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from mcp.db.base import Base # Your SQLAlchemy Base
from mcp.core.config import settings
from mcp.api.main import app # Your FastAPI app
from mcp.db.session import get_db # The dependency we want to override

# Use a separate test database (e.g., SQLite in-memory or a dedicated test PostgreSQL DB)
# For simplicity, using SQLite in-memory here.
# Ensure your DATABASE_URL in config.py is not used directly for tests unless it points to a test DB.
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
# If you want to test against a PostgreSQL test DB:
# SQLALCHEMY_TEST_DATABASE_URL = settings.DATABASE_URL.replace("mcpdb_dev", "mcpdb_test") 
# Ensure this test DB exists and Alembic migrations can be run against it.

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed only for SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Yields a SQLAlchemy engine for the test session. Creates all tables."""
    Base.metadata.create_all(bind=engine) # Create tables for the test session
    yield engine
    Base.metadata.drop_all(bind=engine) # Drop tables after tests

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for a single test function. Rolls back changes after test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback() # Rollback any changes made during the test
        connection.close()

@pytest.fixture(scope="function")
def test_client(db_session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient that uses the test database session."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close() # Ensure session is closed by dependency too
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    del app.dependency_overrides[get_db] # Clean up override
