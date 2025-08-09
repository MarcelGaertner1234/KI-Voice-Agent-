"""User service."""

from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import Session, select

from api.models.user import User, Role
from api.schemas.request.user import UserCreate, UserUpdate
from api.schemas.request.auth import UserRegister
from api.services.auth import AuthService
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserService:
    """User service for user management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)
    
    async def create_user(self, user_data: UserRegister) -> User:
        """Create a new user."""
        # Get default role
        statement = select(Role).where(Role.name == "user")
        default_role = self.db.exec(statement).first()
        
        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=self.auth_service.get_password_hash(user_data.password),
            role_id=default_role.id if default_role else None,
            organization_id=None,  # Will be set when organization is created
            language=user_data.language or "de",
            timezone=user_data.timezone or "Europe/Berlin",
            phone_number=user_data.phone_number,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User created: {user.email}")
        return user
    
    async def create_user_with_organization(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organization_name: Optional[str] = None
    ) -> User:
        """Create a new user with organization if provided."""
        from api.models.organization import Organization
        
        # Get default role
        statement = select(Role).where(Role.name == "user")
        default_role = self.db.exec(statement).first()
        
        # Create organization if name provided
        organization = None
        if organization_name:
            organization = Organization(
                name=organization_name,
                plan_type="trial",
                is_active=True
            )
            self.db.add(organization)
            self.db.commit()
            self.db.refresh(organization)
        
        # Create user
        user = User(
            email=email,
            full_name=f"{first_name} {last_name}",
            hashed_password=self.auth_service.get_password_hash(password),
            role_id=default_role.id if default_role else None,
            organization_id=organization.id if organization else None,
            language="de",
            timezone="Europe/Berlin",
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User created with organization: {user.email}")
        return user
    
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
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
        user_id: uuid.UUID,
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
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Soft delete user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.soft_delete()
        self.db.add(user)
        self.db.commit()
        
        logger.info(f"User deleted: {user.email}")
        return True
    
    async def verify_user(self, user_id: uuid.UUID) -> Optional[User]:
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