# API Design

This document describes the RESTful API endpoints, TypeScript types, and FastAPI
router implementations.

**Related Documents:**

- [System Design](./SYSTEM_DESIGN.md) - Overall architecture
- [API Reference](../api/API_REFERENCE.md) - Detailed API documentation

---

## Table of Contents

1. [RESTful Endpoints](#restful-endpoints)
2. [TypeScript API Types](#typescript-api-types)
3. [FastAPI Router Example](#fastapi-router-example)

---

## RESTful Endpoints

```
Base URL: /api/v1

# ==========================================
# Hooks
# ==========================================

GET    /hooks
       List all hooks with status and schedule info
       Response: { hooks: [...] }

GET    /hooks/{hook_id}
       Get hook details including config and recent runs
       Response: { hook: {...}, recent_jobs: [...] }

POST   /hooks/{hook_id}/run
       Trigger manual hook execution
       Body: { manager_name: "מגדל", email: "user@example.com", ... }
       Response: { job_id: "uuid", status: "queued" }

PATCH  /hooks/{hook_id}/config
       Update hook parameters (admin only)
       Body: { parameters: {...} }
       Response: { hook: {...} }

# ==========================================
# Jobs
# ==========================================

GET    /jobs
       List jobs with pagination and filters
       Query: ?hook_id=X&status=X&page=1&limit=20
       Response: { jobs: [...], total: N, page: 1 }

GET    /jobs/{job_id}
       Get job status and results
       Response: { job: {...}, checks: [...] }

GET    /jobs/{job_id}/stream
       SSE endpoint for real-time progress updates
       Response: Server-Sent Events

GET    /jobs/{job_id}/download
       Download job output file (Excel report)
       Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

DELETE /jobs/{job_id}
       Cancel a running job
       Response: { success: true }

# ==========================================
# Schedules
# ==========================================

GET    /schedules
       List all hook schedules
       Response: { schedules: [...] }

PATCH  /schedules/{hook_id}
       Update hook schedule
       Body: { enabled: true, cron: "0 9 5 * *" }
       Response: { schedule: {...} }

# ==========================================
# Managers
# ==========================================

GET    /managers
       List all fund managers
       Response: { managers: [...] }

GET    /managers/{manager_id}
       Get manager details and recent jobs
       Response: { manager: {...}, recent_jobs: [...] }

# ==========================================
# Health
# ==========================================

GET    /health
       Health check with dependency status
       Response: { status: "healthy", checks: {...} }

GET    /health/ready
       Readiness probe for container orchestration
       Response: { ready: true }
```

---

## TypeScript API Types

```typescript
// apps/web/src/api/types.ts

// ==========================================
// Hooks
// ==========================================

export interface Hook {
  id: string
  name: string
  name_he: string
  description: string
  status: 'active' | 'development' | 'specification'
  schedule: HookSchedule
  checks: HookCheck[]
  parameters: Record<string, unknown>
}

export interface HookSchedule {
  enabled: boolean
  cron: string | null
  timezone: string
  next_run: string | null // ISO datetime
  last_run: string | null // ISO datetime
}

export interface HookCheck {
  id: string
  name: string
  name_he: string
  description: string
  enabled: boolean
}

// ==========================================
// Jobs
// ==========================================

export interface Job {
  id: string
  hook_id: string
  manager_name: string
  manager_id: string
  status: JobStatus
  trigger: 'scheduled' | 'manual' | 'api'
  progress: JobProgress
  result: JobResult | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export type JobStatus =
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface JobProgress {
  current_check: string | null
  checks_completed: number
  checks_total: number
  percent: number
  message: string
}

export interface JobResult {
  status: 'success' | 'partial' | 'failed'
  message: string
  checks: CheckResult[]
  output_file: string | null
  email_sent: boolean
  email_recipients: string[]
  duration_seconds: number
}

export interface CheckResult {
  check_id: string
  check_name: string
  check_name_he: string
  status: 'pass' | 'fail' | 'warning' | 'skipped'
  message: string
  findings_count: number
  duration_ms: number
}

// ==========================================
// Managers
// ==========================================

export interface Manager {
  id: string
  key: string
  name_he: string
  name_en: string
  enabled: boolean
}

// ==========================================
// API Requests
// ==========================================

export interface RunHookRequest {
  manager_name: string
  email: string
  price_threshold?: number
  skip_tase_prices?: boolean
}

export interface UpdateScheduleRequest {
  enabled?: boolean
  cron?: string
}

// ==========================================
// API Responses
// ==========================================

export interface HooksResponse {
  hooks: Hook[]
}

export interface JobsResponse {
  jobs: Job[]
  total: number
  page: number
  limit: number
}

export interface RunHookResponse {
  job_id: string
  status: 'queued'
  message: string
}
```

---

## FastAPI Router Example

```python
# apps/api/src/routers/hooks.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

from ..services.hook_runner import HookRunner
from ..services.job_service import JobService
from ..dependencies import get_hook_config

router = APIRouter(prefix="/hooks", tags=["hooks"])

class RunHookRequest(BaseModel):
    manager_name: str
    email: EmailStr
    price_threshold: Optional[float] = None
    skip_tase_prices: Optional[bool] = True

class RunHookResponse(BaseModel):
    job_id: UUID
    status: str = "queued"
    message: str

@router.get("")
async def list_hooks():
    """List all available hooks with their status and schedules."""
    hooks = await get_all_hooks_with_status()
    return {"hooks": hooks}

@router.get("/{hook_id}")
async def get_hook(hook_id: str):
    """Get hook details including configuration and recent runs."""
    hook = await get_hook_config(hook_id)
    if not hook:
        raise HTTPException(status_code=404, detail=f"Hook '{hook_id}' not found")

    recent_jobs = await JobService.get_recent_by_hook(hook_id, limit=10)
    return {"hook": hook, "recent_jobs": recent_jobs}

@router.post("/{hook_id}/run", response_model=RunHookResponse)
async def run_hook(
    hook_id: str,
    request: RunHookRequest,
    background_tasks: BackgroundTasks
):
    """Trigger manual hook execution."""
    hook_config = await get_hook_config(hook_id)
    if not hook_config:
        raise HTTPException(status_code=404, detail=f"Hook '{hook_id}' not found")

    # Create job record
    job = await JobService.create(
        hook_id=hook_id,
        manager_name=request.manager_name,
        trigger="manual",
        input_data=request.model_dump()
    )

    # Queue background execution
    background_tasks.add_task(
        HookRunner.execute,
        job_id=job.id,
        hook_id=hook_id,
        input_data=request.model_dump()
    )

    return RunHookResponse(
        job_id=job.id,
        status="queued",
        message=f"Job queued for {request.manager_name}"
    )
```

---

**Next:** [Deployment](./DEPLOYMENT.md)
