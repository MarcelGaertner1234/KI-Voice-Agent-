"""Authentication request schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str = Field(min_length=6)


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
    organization_name: Optional[str] = None
    phone_number: Optional[str] = None
    language: str = Field(default="de")
    timezone: str = Field(default="Europe/Berlin")


class PasswordReset(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(min_length=8)


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(min_length=8)