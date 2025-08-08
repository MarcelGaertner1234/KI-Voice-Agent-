"""Health check endpoints."""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlmodel import Session, text

from api.config import get_settings
from api.utils.database import get_db

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
    }


@router.get("/health/ready", response_model=Dict[str, Any])
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check with database connectivity."""
    checks = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Check database
    try:
        db.exec(text("SELECT 1"))
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["status"] = "not ready"
        checks["checks"]["database"] = f"error: {str(e)}"
    
    # TODO: Check Redis connectivity
    # TODO: Check external services (Twilio, OpenAI, etc.)
    
    return checks


@router.get("/health/live", response_model=Dict[str, Any])
async def liveness_check():
    """Liveness check."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }