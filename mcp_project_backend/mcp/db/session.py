"""
Database session management with connection pooling, retries, and health checks.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, Optional
from contextlib import contextmanager
import time
import logging

from mcp.core.settings import settings
from mcp.monitoring.performance import performance_monitor

# Database connection pool configuration
POOL_SIZE = 20
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30
POOL_RECYCLE = 3600  # Recycle connections after 1 hour

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Create a SQLAlchemy engine instance with connection pooling
engine_args = {}
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args.update({
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_timeout": POOL_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
        "pool_pre_ping": True,
        "pool_use_lifo": True
    })

engine = create_engine(settings.DATABASE_URL, **engine_args)

# Create a SessionLocal class to generate database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    
    Includes connection retries and health checks.
    """
    db = None
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            db = SessionLocal()
            # Test connection
            db.execute("SELECT 1")
            break
        except SQLAlchemyError as e:
            retries += 1
            performance_monitor.increment_error("db_connection", str(e))
            logging.error(f"Database connection failed (attempt {retries}/{MAX_RETRIES}): {e}")
            
            if retries < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise
        finally:
            if db:
                db.close()
    
    try:
        yield db
    finally:
        if db:
            db.close()

@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with error handling.
    """
    db = None
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        performance_monitor.increment_error("db_transaction", str(e))
        raise
    finally:
        if db:
            db.close()

def check_db_health() -> bool:
    """
    Check database connection health.
    """
    try:
        with db_session() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        performance_monitor.increment_error("db_health_check", str(e))
        return False
