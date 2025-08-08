"""Organization management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.dependencies import get_current_active_user, get_organization_id
from api.utils.database import get_db
from api.models.user import User
from api.models.organization import Organization
from api.schemas.request.organization import OrganizationCreate, OrganizationUpdate
from api.schemas.response.organization import OrganizationResponse
from api.services.organization import OrganizationService

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new organization."""
    org_service = OrganizationService(db)
    organization = await org_service.create_organization(org_data, current_user.id)
    return organization


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's organization."""
    org_service = OrganizationService(db)
    organization = await org_service.get_by_id(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization


@router.put("/me", response_model=OrganizationResponse)
async def update_my_organization(
    org_update: OrganizationUpdate,
    organization_id: str = Depends(get_organization_id),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update current user's organization."""
    org_service = OrganizationService(db)
    
    # Check if user has permission to update organization
    # TODO: Implement proper permission checking
    
    organization = await org_service.update_organization(organization_id, org_update)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization