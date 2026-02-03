# Additional Requirements

This document covers job history/audit logging, real-time progress updates,
notification system, health checks, and rate limiting.

**Related Documents:**

- [API Design](./API_DESIGN.md) - API endpoints
- [System Design](./SYSTEM_DESIGN.md) - Overall architecture

---

## Table of Contents

1. [Job History & Audit Log](#job-history--audit-log)
2. [Real-Time Progress Updates (SSE)](#real-time-progress-updates-sse)
3. [Notification System](#notification-system)
4. [Health Checks & Monitoring](#health-checks--monitoring)
5. [Rate Limiting](#rate-limiting)

---

## Job History & Audit Log

### Database Schema

```python
# apps/api/src/db/models.py

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
import json

class Job(SQLModel, table=True):
    """Job execution record for audit trail."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hook_id: str = Field(index=True)
    manager_id: Optional[str] = Field(default=None, index=True)
    manager_name: str

    # Execution info
    status: str = Field(default="queued", index=True)  # queued, running, completed, failed, cancelled
    trigger: str  # scheduled, manual, api
    triggered_by: Optional[str] = None  # email or API key identifier

    # Input/Output
    input_data: str = Field(default="{}")  # JSON
    result_summary: Optional[str] = None   # JSON
    output_path: Optional[str] = None
    error_message: Optional[str] = None

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Relationships
    logs: List["JobLog"] = Relationship(back_populates="job")

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def input_dict(self) -> dict:
        return json.loads(self.input_data)

    @property
    def result_dict(self) -> Optional[dict]:
        if self.result_summary:
            return json.loads(self.result_summary)
        return None


class JobLog(SQLModel, table=True):
    """Detailed job execution logs."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    job_id: UUID = Field(foreign_key="job.id", index=True)

    level: str  # DEBUG, INFO, WARNING, ERROR
    check_id: Optional[str] = None
    message: str
    details: Optional[str] = None  # JSON for structured data

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    job: Job = Relationship(back_populates="logs")


class ScheduleOverride(SQLModel, table=True):
    """Track manual schedule changes (for audit)."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hook_id: str = Field(index=True)

    previous_cron: Optional[str]
    new_cron: Optional[str]
    previous_enabled: bool
    new_enabled: bool

    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
```

---

## Real-Time Progress Updates (SSE)

### Backend Implementation

```python
# apps/api/src/routers/jobs.py

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """
    Server-Sent Events endpoint for real-time job progress.

    Events:
    - progress: { status, current_check, percent, message }
    - check_complete: { check_id, status, findings_count }
    - complete: { status, message, output_file }
    - error: { message }
    """
    async def event_generator():
        while True:
            job = await JobService.get(job_id)

            if job is None:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": "Job not found"})
                }
                break

            # Send progress update
            yield {
                "event": "progress",
                "data": json.dumps({
                    "status": job.status,
                    "current_check": job.current_check,
                    "checks_completed": job.checks_completed,
                    "checks_total": job.checks_total,
                    "percent": job.progress_percent,
                    "message": job.progress_message
                })
            }

            # Check for completion
            if job.status in ("completed", "failed", "cancelled"):
                yield {
                    "event": "complete",
                    "data": json.dumps({
                        "status": job.status,
                        "message": job.result_dict.get("message") if job.result_dict else None,
                        "output_file": job.output_path,
                        "duration_seconds": job.duration_seconds
                    })
                }
                break

            await asyncio.sleep(1)  # Poll every second

    return EventSourceResponse(event_generator())
```

### Frontend Hook

```typescript
// apps/web/src/hooks/useJobStream.ts

import { useState, useEffect, useCallback } from 'react'

interface JobProgress {
  status: string
  current_check: string | null
  checks_completed: number
  checks_total: number
  percent: number
  message: string
}

export function useJobStream(jobId: string | null) {
  const [progress, setProgress] = useState<JobProgress | null>(null)
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) return

    const eventSource = new EventSource(`/api/v1/jobs/${jobId}/stream`)

    eventSource.addEventListener('progress', (e) => {
      setProgress(JSON.parse(e.data))
    })

    eventSource.addEventListener('complete', (e) => {
      setProgress(JSON.parse(e.data))
      setIsComplete(true)
      eventSource.close()
    })

    eventSource.addEventListener('error', (e) => {
      setError('Connection lost')
      eventSource.close()
    })

    return () => {
      eventSource.close()
    }
  }, [jobId])

  return { progress, isComplete, error }
}
```

---

## Notification System

```yaml
# config/notifications.yaml

version: '1.0'

channels:
  email:
    enabled: true
    provider: 'resend' # resend | smtp | console

  slack:
    enabled: true
    webhook_url: '${SLACK_WEBHOOK_URL}'

  webhook:
    enabled: false
    url: '${CUSTOM_WEBHOOK_URL}'

templates:
  job_success:
    email:
      subject: '✅ {hook_name} - {manager_name} - Completed'
    slack:
      text: '✅ *{hook_name}* completed for *{manager_name}*'
      color: 'good'

  job_partial:
    email:
      subject: '⚠️ {hook_name} - {manager_name} - Completed with warnings'
    slack:
      text:
        '⚠️ *{hook_name}* for *{manager_name}* completed with {warning_count}
        warnings'
      color: 'warning'

  job_failed:
    email:
      subject: '❌ {hook_name} - {manager_name} - Failed'
    slack:
      text: '❌ *{hook_name}* failed for *{manager_name}*: {error_message}'
      color: 'danger'

routing:
  # Which channels to use for each event type
  on_success:
    - email

  on_partial:
    - email
    - slack

  on_failure:
    - email
    - slack

recipients:
  default:
    - 'elay.g@82labs.io'

  alerts:
    - 'ops@82labs.io'
```

---

## Health Checks & Monitoring

```python
# apps/api/src/routers/health.py

from fastapi import APIRouter
from datetime import datetime
import asyncio

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Comprehensive health check with dependency status.
    """
    checks = await asyncio.gather(
        check_database(),
        check_redis(),
        check_apify(),
        check_email_service(),
        return_exceptions=True
    )

    db_status, redis_status, apify_status, email_status = checks

    all_healthy = all(
        isinstance(c, dict) and c.get("healthy", False)
        for c in checks
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": db_status if isinstance(db_status, dict) else {"healthy": False, "error": str(db_status)},
            "redis": redis_status if isinstance(redis_status, dict) else {"healthy": False, "error": str(redis_status)},
            "apify": apify_status if isinstance(apify_status, dict) else {"healthy": False, "error": str(apify_status)},
            "email": email_status if isinstance(email_status, dict) else {"healthy": False, "error": str(email_status)},
        }
    }

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes/container orchestration.
    Returns 200 if the service is ready to accept traffic.
    """
    # Check critical dependencies only
    db_ok = await check_database_connection()

    if not db_ok:
        return {"ready": False}, 503

    return {"ready": True}

@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe - just confirms the process is running.
    """
    return {"alive": True}
```

---

## Rate Limiting

```python
# packages/shared/src/mizrahi_shared/rate_limit.py

import asyncio
from functools import wraps
from typing import Callable, Any

# Semaphores for external service rate limiting
_SEMAPHORES = {
    "apify": asyncio.Semaphore(3),      # Max 3 concurrent Apify calls
    "tase": asyncio.Semaphore(1),        # Max 1 concurrent TASE scrape (be gentle)
    "email": asyncio.Semaphore(5),       # Max 5 concurrent email sends
}

def rate_limited(service: str):
    """
    Decorator to rate limit calls to external services.

    Usage:
        @rate_limited("apify")
        async def call_apify_actor(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            semaphore = _SEMAPHORES.get(service)
            if semaphore is None:
                return await func(*args, **kwargs)

            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper
    return decorator
```

---

**Next:** [Migration Plan](./MIGRATION_PLAN.md)
