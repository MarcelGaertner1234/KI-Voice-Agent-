"""Organization model."""

from typing import Optional, List
from sqlmodel import Field, Relationship
import uuid

from api.models.base import BaseModel


class Organization(BaseModel, table=True):
    """Organization model for multi-tenancy."""
    
    __tablename__ = "organizations"
    
    # Basic info
    name: str = Field(nullable=False, index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    
    # Contact info
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: str = Field(default="DE")
    
    # Business info
    business_type: Optional[str] = None  # restaurant, medical, retail, etc.
    business_hours: dict = Field(default_factory=dict, sa_column_kwargs={"type": "JSON"})
    timezone: str = Field(default="Europe/Berlin")
    
    # Subscription
    subscription_plan: str = Field(default="free")
    subscription_status: str = Field(default="active")
    trial_ends_at: Optional[str] = None
    
    # Settings
    settings: dict = Field(default_factory=dict, sa_column_kwargs={"type": "JSON"})
    features: dict = Field(default_factory=dict, sa_column_kwargs={"type": "JSON"})
    
    # Limits
    max_agents: int = Field(default=1)
    max_calls_per_month: int = Field(default=100)
    max_minutes_per_month: int = Field(default=500)
    
    # Usage
    current_month_calls: int = Field(default=0)
    current_month_minutes: int = Field(default=0)
    
    # Relations
    users: List["User"] = Relationship(back_populates="organization")
    agents: List["Agent"] = Relationship(back_populates="organization")
    customers: List["Customer"] = Relationship(back_populates="organization")
    webhooks: List["Webhook"] = Relationship(back_populates="organization")