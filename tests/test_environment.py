"""
Test environment setup and configuration.
"""
import os
import tempfile
from pathlib import Path
from mcp.core.config import Settings
from mcp.db.base import Base, metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment variables
os.environ['TESTING'] = 'true'
os.environ['DEBUG'] = 'true'

# Create temporary database file
db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
os.environ['DATABASE_URL'] = f'sqlite:///{db_file.name}'
os.environ['API_V1_STR'] = '/api/v1'

# Create test directories if they don't exist
test_dirs = [
    'tests/data',
    'tests/reports',
    'tests/logs',
    'tests/coverage'
]

for dir_path in test_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# Initialize settings with test configuration
settings = Settings()

# Create database engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Print test configuration for debugging
print("Test Configuration:")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"API Version: {settings.API_V1_STR}")

# Cleanup function to be called after tests
def cleanup():
    """Cleanup test database and files."""
    try:
        # Close database connections
        engine.dispose()
        
        # Remove temporary database file
        os.unlink(db_file.name)
        
        print("Test cleanup completed successfully")
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")

# Register cleanup function to be called when tests finish
import atexit
atexit.register(cleanup)
