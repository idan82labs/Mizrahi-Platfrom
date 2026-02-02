"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness probe for container orchestration."""
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """Liveness probe - confirms process is running."""
    return {"alive": True}
