"""User model."""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
import uuid

from api.models.base import BaseModel


class User(BaseModel, table=True):
    """User model."""
    
    __tablename__ = "users"
    
    # Basic info
    email: str = Field(unique=True, index=True, nullable=False)
    full_name: str = Field(nullable=False)
    hashed_password: str = Field(nullable=False)
    
    # Status
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    verified_at: Optional[datetime] = None
    
    # Organization
    organization_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="organizations.id"
    )
    organization: Optional["Organization"] = Relationship(back_populates="users")
    
    # Role
    role_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="roles.id"
    )
    role: Optional["Role"] = Relationship(back_populates="users")
    
    # Settings
    language: str = Field(default="de")
    timezone: str = Field(default="Europe/Berlin")
    phone_number: Optional[str] = None
    
    # Relations
    api_keys: List["APIKey"] = Relationship(back_populates="user")
    sessions: List["UserSession"] = Relationship(back_populates="user")
    
    class Config:
        validate_assignment = True


class Role(BaseModel, table=True):
    """Role model for permissions."""
    
    __tablename__ = "roles"
    
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    permissions: dict = Field(default_factory=dict, sa_column_kwargs={"type": "JSON"})
    is_system: bool = Field(default=False)  # System roles can't be deleted
    
    # Relations
    users: List["User"] = Relationship(back_populates="role")


class APIKey(BaseModel, table=True):
    """API Key for programmatic access."""
    
    __tablename__ = "api_keys"
    
    name: str = Field(nullable=False)
    key_hash: str = Field(unique=True, index=True)
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list, sa_column_kwargs={"type": "JSON"})
    
    # Relations
    user_id: uuid.UUID = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="api_keys")


class UserSession(BaseModel, table=True):
    """Active user sessions."""
    
    __tablename__ = "user_sessions"
    
    token_hash: str = Field(unique=True, index=True)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: datetime = Field(nullable=False)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    user_id: uuid.UUID = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="sessions")