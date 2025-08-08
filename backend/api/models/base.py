"""Base model for all database models."""

from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model with common fields."""
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    
    class Config:
        validate_assignment = True
        
    def soft_delete(self):
        """Soft delete the record."""
        self.deleted_at = datetime.utcnow()