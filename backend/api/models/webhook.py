"""Webhook model."""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, Relationship
import uuid

from api.models.base import BaseModel


class Webhook(BaseModel, table=True):
    """Webhook configuration."""
    
    __tablename__ = "webhooks"
    
    # Configuration
    name: str = Field(nullable=False)
    url: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    
    # Events to listen for
    events: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Authentication
    secret: Optional[str] = None
    headers: dict = Field(
        default_factory=dict,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Retry configuration
    max_retries: int = Field(default=3)
    retry_delay: int = Field(default=60)  # seconds
    timeout: int = Field(default=30)  # seconds
    
    # Stats
    last_triggered_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_message: Optional[str] = None
    total_calls: int = Field(default=0)
    failed_calls: int = Field(default=0)
    
    # Relations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    organization: "Organization" = Relationship(back_populates="webhooks")
    
    events_log: List["WebhookEvent"] = Relationship(back_populates="webhook")


class WebhookEvent(BaseModel, table=True):
    """Webhook event delivery log."""
    
    __tablename__ = "webhook_events"
    
    # Event info
    event_type: str = Field(nullable=False, index=True)
    event_data: dict = Field(
        nullable=False,
        sa_column_kwargs={"type": "JSON"}
    )
    
    # Delivery info
    status: str = Field(default="pending", index=True)  # pending/success/failed
    attempts: int = Field(default=0)
    
    # Response
    response_status_code: Optional[int] = None
    response_headers: Optional[dict] = Field(
        default=None,
        sa_column_kwargs={"type": "JSON"}
    )
    response_body: Optional[str] = None
    
    # Timing
    scheduled_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    
    # Error info
    error_message: Optional[str] = None
    
    # Relations
    webhook_id: uuid.UUID = Field(foreign_key="webhooks.id", index=True)
    webhook: "Webhook" = Relationship(back_populates="events_log")