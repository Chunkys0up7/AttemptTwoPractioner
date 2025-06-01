from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as DBEnum
from sqlalchemy.sql import func
from enum import Enum
from mcp.db.base import Base

class UserRoleEnum(str, Enum):
    """
    Enum for user roles in the system.
    """
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class User(Base):
    """
    SQLAlchemy model for the User table.
    Represents a user in the system with authentication and role information.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role_name = Column(DBEnum(UserRoleEnum, name="user_role_enum"), default=UserRoleEnum.VIEWER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
