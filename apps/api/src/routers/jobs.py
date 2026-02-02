"""
Jobs API endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class JobInfo(BaseModel):
    """Job information."""
    id: str
    hook_id: str
    manager_name: str
    status: str
    trigger: str
    created_at: str
    completed_at: Optional[str] = None


class JobsResponse(BaseModel):
    """Response for jobs list."""
    jobs: List[JobInfo]
    total: int
    page: int
    limit: int


@router.get("/jobs")
async def list_jobs(
    hook_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    """
    List jobs with optional filtering.

    In a full implementation, this would query the database.
    For now, returns an empty list as placeholder.
    """
    return {
        "jobs": [],
        "total": 0,
        "page": page,
        "limit": limit,
    }


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get job details by ID.

    In a full implementation, this would query the database.
    """
    raise HTTPException(
        status_code=404,
        detail=f"Job '{job_id}' not found (job storage not yet implemented)",
    )


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job.

    In a full implementation, this would update the job status.
    """
    raise HTTPException(
        status_code=404,
        detail=f"Job '{job_id}' not found (job storage not yet implemented)",
    )
