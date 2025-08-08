"""Database utilities."""

from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool

from api.config import get_settings

settings = get_settings()

# Create engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite for testing
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL for production
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
    )


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session