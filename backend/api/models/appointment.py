"""Appointment model."""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship
import uuid

from api.models.base import BaseModel


class Appointment(BaseModel, table=True):
    """Appointment booking."""
    
    __tablename__ = "appointments"
    
    # Appointment details
    title: str = Field(nullable=False)
    description: Optional[str] = None
    appointment_type: Optional[str] = None  # consultation/service/follow-up
    
    # Timing
    start_time: datetime = Field(nullable=False, index=True)
    end_time: datetime = Field(nullable=False)
    duration_minutes: int = Field(default=30)
    timezone: str = Field(default="Europe/Berlin")
    
    # Status
    status: str = Field(default="scheduled", index=True)  # scheduled/confirmed/cancelled/completed/no-show
    confirmation_sent: bool = Field(default=False)
    reminder_sent: bool = Field(default=False)
    
    # Location
    location_type: str = Field(default="on-site")  # on-site/phone/video
    location_details: Optional[str] = None
    meeting_url: Optional[str] = None
    
    # Resources
    resource_id: Optional[uuid.UUID] = None  # Staff member, room, etc.
    resource_name: Optional[str] = None
    
    # Notes
    customer_notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Cancellation
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    # Relations
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True)
    customer: "Customer" = Relationship(back_populates="appointments")
    
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    
    # Call that created this appointment
    created_by_call_id: Optional[uuid.UUID] = Field(foreign_key="calls.id")
    
    # Metadata
    metadata: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    
    class Config:
        validate_assignment = True


class AppointmentSlot(BaseModel, table=True):
    """Available appointment slots."""
    
    __tablename__ = "appointment_slots"
    
    # Slot info
    date: datetime = Field(nullable=False, index=True)
    start_time: str = Field(nullable=False)  # HH:MM format
    end_time: str = Field(nullable=False)
    
    # Availability
    total_slots: int = Field(default=1)
    booked_slots: int = Field(default=0)
    is_available: bool = Field(default=True)
    
    # Resource
    resource_id: Optional[uuid.UUID] = None
    resource_name: Optional[str] = None
    
    # Service types
    service_types: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Relations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    
    class Config:
        validate_assignment = True


class Calendar(BaseModel, table=True):
    """Calendar configuration."""
    
    __tablename__ = "calendars"
    
    name: str = Field(nullable=False)
    description: Optional[str] = None
    
    # Working hours per day
    working_hours: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Break times
    break_times: List[dict] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Holidays and special dates
    holidays: List[dict] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Booking rules
    min_advance_booking: int = Field(default=0)  # minutes
    max_advance_booking: int = Field(default=10080)  # minutes (1 week)
    slot_duration: int = Field(default=30)  # minutes
    buffer_time: int = Field(default=0)  # minutes between appointments
    
    # Relations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    resource_id: Optional[uuid.UUID] = None