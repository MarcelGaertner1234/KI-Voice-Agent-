"""Customer model."""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship
import uuid

from api.models.base import BaseModel


class Customer(BaseModel, table=True):
    """Customer profile."""
    
    __tablename__ = "customers"
    
    # Basic info
    phone_number: str = Field(index=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    
    # Additional info
    company: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    language: str = Field(default="de")
    
    # Contact preferences
    preferred_contact_method: str = Field(default="phone")  # phone/email/sms
    do_not_call: bool = Field(default=False)
    marketing_consent: bool = Field(default=False)
    
    # Address
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: str = Field(default="DE")
    
    # CRM fields
    customer_type: Optional[str] = None  # lead/customer/vip
    source: Optional[str] = None  # website/referral/cold-call/etc
    tags: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    custom_fields: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Metrics
    lifetime_value: float = Field(default=0.0)
    total_orders: int = Field(default=0)
    total_appointments: int = Field(default=0)
    last_contact_at: Optional[datetime] = None
    
    # Notes
    internal_notes: Optional[str] = None
    
    # Relations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    organization: "Organization" = Relationship(back_populates="customers")
    
    calls: List["Call"] = Relationship(back_populates="customer")
    appointments: List["Appointment"] = Relationship(back_populates="customer")
    interactions: List["CustomerInteraction"] = Relationship(back_populates="customer")
    
    # Unique constraint per organization
    class Config:
        validate_assignment = True
        # TODO: Add unique constraint for (organization_id, phone_number)


class CustomerInteraction(BaseModel, table=True):
    """Customer interaction history."""
    
    __tablename__ = "customer_interactions"
    
    interaction_type: str = Field(nullable=False)  # call/email/sms/note
    channel: str = Field(nullable=False)  # phone/email/web/api
    direction: str = Field(default="inbound")  # inbound/outbound
    
    subject: Optional[str] = None
    content: Optional[str] = None
    
    # Outcome
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    
    # Relations
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True)
    customer: "Customer" = Relationship(back_populates="interactions")
    
    agent_id: Optional[uuid.UUID] = Field(foreign_key="agents.id")
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id")
    
    # Reference to related records
    call_id: Optional[uuid.UUID] = Field(foreign_key="calls.id")
    appointment_id: Optional[uuid.UUID] = Field(foreign_key="appointments.id")