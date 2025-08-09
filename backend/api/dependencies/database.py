"""Database dependency."""

from typing import Generator
from sqlmodel import Session
from api.utils.database import engine


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency to get DB session.
    
    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session