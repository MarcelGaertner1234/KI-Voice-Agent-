"""Organization service."""

from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import Session, select
import re

from api.models.organization import Organization
from api.schemas.request.organization import OrganizationCreate, OrganizationUpdate
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class OrganizationService:
    """Organization service for multi-tenancy."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name."""
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug
    
    async def create_organization(
        self,
        org_create: OrganizationCreate,
        owner_id: uuid.UUID
    ) -> Organization:
        """Create a new organization."""
        # Generate unique slug
        base_slug = self._generate_slug(org_create.name)
        slug = base_slug
        counter = 1
        
        while self.db.exec(
            select(Organization).where(Organization.slug == slug)
        ).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create organization
        organization = Organization(
            name=org_create.name,
            slug=slug,
            description=org_create.description,
            email=org_create.email,
            phone=org_create.phone,
            website=org_create.website,
            business_type=org_create.business_type,
            address_street=org_create.address_street,
            address_city=org_create.address_city,
            address_state=org_create.address_state,
            address_postal_code=org_create.address_postal_code,
            address_country=org_create.address_country or "DE",
            timezone=org_create.timezone or "Europe/Berlin",
        )
        
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        
        # Update owner's organization
        from api.models.user import User
        owner = self.db.get(User, owner_id)
        if owner:
            owner.organization_id = organization.id
            self.db.add(owner)
            self.db.commit()
        
        logger.info(f"Organization created: {organization.name} ({organization.slug})")
        return organization
    
    async def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        """Get organization by ID."""
        statement = select(Organization).where(
            Organization.id == org_id,
            Organization.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        statement = select(Organization).where(
            Organization.slug == slug,
            Organization.deleted_at == None
        )
        return self.db.exec(statement).first()
    
    async def update_organization(
        self,
        org_id: uuid.UUID,
        org_update: OrganizationUpdate
    ) -> Optional[Organization]:
        """Update organization."""
        organization = await self.get_by_id(org_id)
        if not organization:
            return None
        
        # Update fields
        update_data = org_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        organization.updated_at = datetime.utcnow()
        
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        
        logger.info(f"Organization updated: {organization.name}")
        return organization
    
    async def update_usage(
        self,
        org_id: uuid.UUID,
        calls: int = 0,
        minutes: int = 0
    ) -> Optional[Organization]:
        """Update organization usage metrics."""
        organization = await self.get_by_id(org_id)
        if not organization:
            return None
        
        organization.current_month_calls += calls
        organization.current_month_minutes += minutes
        
        self.db.add(organization)
        self.db.commit()
        
        return organization
    
    async def check_limits(self, org_id: uuid.UUID) -> dict:
        """Check if organization has exceeded limits."""
        organization = await self.get_by_id(org_id)
        if not organization:
            return {"allowed": False, "reason": "Organization not found"}
        
        if organization.subscription_status != "active":
            return {"allowed": False, "reason": "Subscription not active"}
        
        if organization.current_month_calls >= organization.max_calls_per_month:
            return {"allowed": False, "reason": "Monthly call limit exceeded"}
        
        if organization.current_month_minutes >= organization.max_minutes_per_month:
            return {"allowed": False, "reason": "Monthly minutes limit exceeded"}
        
        return {"allowed": True}
    
    async def list_organizations(
        self,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """List organizations with optional filtering."""
        statement = select(Organization).where(Organization.deleted_at == None)
        
        if user_id:
            # Filter by user membership
            from api.models.user import User
            user = self.db.get(User, user_id)
            if user and user.organization_id:
                statement = statement.where(Organization.id == user.organization_id)
            else:
                return []
        
        statement = statement.offset(skip).limit(limit)
        return list(self.db.exec(statement).all())
    
    async def delete_organization(self, org_id: uuid.UUID) -> bool:
        """Soft delete organization."""
        organization = await self.get_by_id(org_id)
        if not organization:
            return False
        
        organization.soft_delete()
        self.db.add(organization)
        self.db.commit()
        
        logger.info(f"Organization deleted: {organization.name}")
        return True