"""User request schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserCreate(BaseModel):
    """User creation request."""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
    organization_id: Optional[uuid.UUID] = None
    phone_number: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class UserUpdate(BaseModel):
    """User update request."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    phone_number: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None