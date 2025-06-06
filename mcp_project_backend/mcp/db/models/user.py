from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as DBEnum
from sqlalchemy.sql import func
from enum import Enum
from sqlalchemy.orm import relationship
from datetime import datetime
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
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)

    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="user", cascade="all, delete-orphan")
    created_templates = relationship("WorkflowTemplate", back_populates="creator", cascade="all, delete-orphan")
    created_template_versions = relationship("WorkflowTemplateVersion", back_populates="creator", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
