"""Organization request schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    """Organization creation request."""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    business_type: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: Optional[str] = None
    timezone: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Organization update request."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    business_type: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: Optional[str] = None
    timezone: Optional[str] = None
    business_hours: Optional[dict] = None
    settings: Optional[dict] = None