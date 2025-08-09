"""Simple test script to verify API setup."""

import asyncio
from sqlmodel import Session, create_engine
from api.config import get_settings
from api.models import *  # This creates all tables
from api.utils.database import engine

settings = get_settings()


async def test_api():
    """Test basic API functionality."""
    print("Testing API setup...")
    
    # Create tables
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created")
    
    # Test auth service
    from api.services.auth import AuthService
    with Session(engine) as db:
        auth_service = AuthService(db)
        
        # Test password hashing
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        assert auth_service.verify_password(password, hashed)
        print("✅ Password hashing works")
        
        # Test token creation
        token = auth_service.create_access_token("test-user-id")
        assert token is not None
        print("✅ Token creation works")
    
    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_api())