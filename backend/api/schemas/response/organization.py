"""Organization response schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


class OrganizationResponse(BaseModel):
    """Organization response."""
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    business_type: Optional[str]
    address_street: Optional[str]
    address_city: Optional[str]
    address_state: Optional[str]
    address_postal_code: Optional[str]
    address_country: str
    timezone: str
    business_hours: dict
    subscription_plan: str
    subscription_status: str
    max_agents: int
    max_calls_per_month: int
    max_minutes_per_month: int
    current_month_calls: int
    current_month_minutes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True