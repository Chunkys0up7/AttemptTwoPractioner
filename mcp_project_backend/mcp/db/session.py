"""
Database session management for FastAPI dependencies.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from mcp.core.config import settings

# Create a SQLAlchemy engine instance.
# connect_args are for SQLite. For PostgreSQL, these are not typically needed.
engine_args = {}
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL,
                       pool_pre_ping=True, **engine_args)

# Create a SessionLocal class to generate database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session.

    It ensures the session is closed after the request is finished.
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()
