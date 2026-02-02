"""
Hooks API endpoints.
"""

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr

router = APIRouter()


class RunHookRequest(BaseModel):
    """Request body for running a hook."""
    manager_name: str
    email: str
    price_threshold: Optional[float] = None
    skip_tase_prices: Optional[bool] = True


class RunHookResponse(BaseModel):
    """Response for hook run request."""
    job_id: str
    status: str = "queued"
    message: str


class HookInfo(BaseModel):
    """Hook information."""
    id: str
    name: str
    name_he: str
    description: str
    status: str
    schedule_enabled: bool
    schedule_cron: Optional[str]


@router.get("/hooks")
async def list_hooks():
    """List all available hooks."""
    try:
        from mizrahi_shared.config import get_hooks_config
        hooks_config = get_hooks_config()

        hooks = []
        for hook_id, config in hooks_config.items():
            hooks.append({
                "id": config.id,
                "name": config.name,
                "name_he": config.name_he,
                "description": config.description,
                "status": config.status,
                "schedule_enabled": config.schedule_enabled,
                "schedule_cron": config.schedule_cron,
            })

        return {"hooks": hooks}
    except Exception as e:
        return {"hooks": [], "error": str(e)}


@router.get("/hooks/{hook_id}")
async def get_hook(hook_id: str):
    """Get hook details."""
    try:
        from mizrahi_shared.config import get_hook_config
        config = get_hook_config(hook_id)

        if not config:
            raise HTTPException(status_code=404, detail=f"Hook '{hook_id}' not found")

        return {
            "hook": {
                "id": config.id,
                "name": config.name,
                "name_he": config.name_he,
                "description": config.description,
                "status": config.status,
                "schedule_enabled": config.schedule_enabled,
                "schedule_cron": config.schedule_cron,
                "parameters": config.parameters,
                "checks": [
                    {
                        "id": c.id,
                        "name_he": c.name_he,
                        "description": c.description,
                        "enabled": c.enabled,
                    }
                    for c in config.checks
                ],
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hooks/{hook_id}/run", response_model=RunHookResponse)
async def run_hook(
    hook_id: str,
    request: RunHookRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger a hook execution."""
    try:
        from mizrahi_hooks import get_hook
        from mizrahi_shared.config import get_hook_config

        config = get_hook_config(hook_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Hook '{hook_id}' not found")

        # Create job ID
        job_id = str(uuid4())

        # Queue background execution
        # In a full implementation, this would add to a job queue
        # For now, we'll just return the job ID

        return RunHookResponse(
            job_id=job_id,
            status="queued",
            message=f"Hook '{hook_id}' queued for execution for {request.manager_name}",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
