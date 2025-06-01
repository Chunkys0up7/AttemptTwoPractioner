"""
Pydantic schemas for authentication-related API requests and responses.

These models are used for login, token, and user info endpoints in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role_name: Optional[str] = None

class UserLoginRequest(BaseModel):
    """
    Schema for user login requests.

    Attributes:
        username (EmailStr): User's email address (or str, depending on login mechanism).
        password (str): User's password.
    """
    username: EmailStr = Field(..., description="User's email address.")
    password: str = Field(..., description="User's password.")

class TokenResponse(BaseModel):
    """
    Schema for authentication token responses.

    Attributes:
        access_token (str): The JWT or access token.
        token_type (str): The type of token (e.g., 'bearer').
    """
    access_token: str = Field(..., description="The JWT or access token.")
    token_type: str = Field(..., description="The type of token (e.g., 'bearer').")

class UserRead(BaseModel):
    """
    Schema for reading user information (e.g., after login or for user profile endpoints).

    Attributes:
        id (int): Unique identifier for the user.
        email (EmailStr): User's email address.
        full_name (Optional[str]): User's full name.
        is_active (bool): Whether the user account is active.
        # Add role information if needed.
    """
    id: int = Field(..., description="Unique identifier for the user.")
    email: EmailStr = Field(..., description="User's email address.")
    full_name: Optional[str] = Field(None, description="User's full name.")
    is_active: bool = Field(..., description="Whether the user account is active.")
    # role_name: Optional[str] = Field(None, description="Role of the user (e.g., 'Admin', 'Editor').")

    class Config:
        orm_mode = True
