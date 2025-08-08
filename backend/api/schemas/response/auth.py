"""Authentication response schemas."""

from typing import Optional
from pydantic import BaseModel
import uuid


class Token(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response."""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    organization_id: Optional[uuid.UUID]
    role_id: Optional[uuid.UUID]
    language: str
    timezone: str
    phone_number: Optional[str]
    
    class Config:
        from_attributes = True