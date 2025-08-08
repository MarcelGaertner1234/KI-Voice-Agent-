"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select

from api.config import get_settings
from api.models.user import User
from api.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        scopes: Optional[list] = None
    ) -> str:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "type": "access",
            "scopes": scopes or []
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def create_refresh_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[str]:
        """Verify JWT token and return subject."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != token_type:
                return None
            
            subject: str = payload.get("sub")
            if subject is None:
                return None
            
            return subject
        except JWTError:
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[str]:
        """Verify refresh token."""
        return self.verify_token(token, token_type="refresh")
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password."""
        statement = select(User).where(
            User.email == email,
            User.deleted_at == None
        )
        user = self.db.exec(statement).first()
        
        if not user:
            logger.warning(f"Authentication failed: User not found - {email}")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password - {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: Inactive user - {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        user_id = self.verify_token(token)
        if not user_id:
            return None
        
        statement = select(User).where(
            User.id == user_id,
            User.deleted_at == None
        )
        user = self.db.exec(statement).first()
        
        if not user or not user.is_active:
            return None
        
        return user