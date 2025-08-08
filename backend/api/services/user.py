"""User service."""

from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import Session, select

from api.models.user import User, Role
from api.schemas.request.user import UserCreate, UserUpdate
from api.services.auth import AuthService
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserService:
    """User service for user management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        # Get default role
        statement = select(Role).where(Role.name == "user")
        default_role = self.db.exec(statement).first()
        
        # Create user
        user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=self.auth_service.get_password_hash(user_create.password),
            role_id=default_role.id if default_role else None,
            organization_id=user_create.organization_id,
            language=user_create.language or "de",
            timezone=user_create.timezone or "Europe/Berlin",
            phone_number=user_create.phone_number,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User created: {user.email}")
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        statement = select(User).where(
            User.id == user_id,
            User.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(
            User.email == email,
            User.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def list_users(
        self,
        organization_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """List users with optional filtering."""
        statement = select(User).where(User.deleted_at == None)
        
        if organization_id:
            statement = statement.where(User.organization_id == organization_id)
        
        statement = statement.offset(skip).limit(limit)
        return list(self.db.exec(statement).all())
    
    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate
    ) -> Optional[User]:
        """Update user."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data:
            update_data["hashed_password"] = self.auth_service.get_password_hash(
                update_data.pop("password")
            )
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User updated: {user.email}")
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.soft_delete()
        self.db.add(user)
        self.db.commit()
        
        logger.info(f"User deleted: {user.email}")
        return True
    
    async def verify_user(self, user_id: str) -> Optional[User]:
        """Verify user email."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.is_verified = True
        user.verified_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User verified: {user.email}")
        return user