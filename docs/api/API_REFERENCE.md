# API Reference

This document describes the REST API endpoints for the Mizrahi Compliance Platform.

**Base URL:** `http://localhost:8000` (development) or `https://your-domain.com` (production)

---

## Authentication

Currently, the API does not require authentication. This will be added in a future release.

---

## Endpoints

### Health

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T17:30:00.000000",
  "version": "1.0.0"
}
```

#### GET /health/ready

Readiness probe for container orchestration.

**Response:**
```json
{
  "ready": true
}
```

#### GET /health/live

Liveness probe.

**Response:**
```json
{
  "alive": true
}
```

---

### Hooks

#### GET /api/hooks

List all available hooks with their status and schedule information.

**Response:**
```json
{
  "hooks": [
    {
      "id": "monthly_report",
      "name": "Monthly Report Validation",
      "name_he": "בקרה אוטומטית על דוח חודשי",
      "description": "Validates monthly fund holdings reports against Magna list",
      "status": "active",
      "schedule_enabled": true,
      "schedule_cron": "0 9 5 * *"
    },
    {
      "id": "special_transactions",
      "name": "Special Transactions Validation",
      "name_he": "בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה",
      "description": "Validates coordinated/off-exchange trades",
      "status": "development",
      "schedule_enabled": false,
      "schedule_cron": "0 10 5 * *"
    }
  ]
}
```

---

#### GET /api/hooks/{hook_id}

Get detailed information about a specific hook.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hook_id | path | Hook identifier (e.g., "monthly_report") |

**Response:**
```json
{
  "hook": {
    "id": "monthly_report",
    "name": "Monthly Report Validation",
    "name_he": "בקרה אוטומטית על דוח חודשי",
    "description": "Validates monthly fund holdings reports against Magna list",
    "status": "active",
    "schedule_enabled": true,
    "schedule_cron": "0 9 5 * *",
    "parameters": {
      "price_variance_threshold": 7.5,
      "unusual_asset_types": [16, 21, 22, 23, 24, ...],
      "required_combinations": { "111": [38, 42, 45, 47, 49, 56], ... }
    },
    "checks": [
      {
        "id": "completeness",
        "name_he": "בדיקת שלמות",
        "description": "Cross-reference Magna vs Manager reports",
        "enabled": true
      },
      ...
    ]
  }
}
```

**Error Response (404):**
```json
{
  "detail": "Hook 'unknown_hook' not found"
}
```

---

#### POST /api/hooks/{hook_id}/run

Trigger a hook execution for a specific fund manager.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hook_id | path | Hook identifier |

**Request Body:**
```json
{
  "manager_name": "סיגמא",
  "email": "user@example.com",
  "price_threshold": 5.0,
  "skip_tase_prices": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| manager_name | string | Yes | Hebrew name of fund manager |
| email | string | Yes | Recipient email(s), semicolon-separated |
| price_threshold | number | No | Price variance threshold % (default: from config) |
| skip_tase_prices | boolean | No | Skip TASE price scraping (default: true) |

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Hook 'monthly_report' queued for execution for סיגמא"
}
```

---

### Jobs

#### GET /api/jobs

List jobs with optional filtering and pagination.

**Query Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hook_id | string | Filter by hook ID |
| status | string | Filter by status (queued, running, completed, failed) |
| page | integer | Page number (default: 1) |
| limit | integer | Items per page (default: 20) |

**Response:**
```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "hook_id": "monthly_report",
      "manager_name": "סיגמא",
      "status": "completed",
      "trigger": "manual",
      "created_at": "2026-02-02T17:30:00.000000",
      "completed_at": "2026-02-02T17:35:00.000000"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

---

#### GET /api/jobs/{job_id}

Get detailed status and results of a specific job.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| job_id | path | Job UUID |

**Response (completed):**
```json
{
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "hook_id": "monthly_report",
    "manager_name": "סיגמא",
    "manager_id": "10048",
    "status": "completed",
    "trigger": "manual",
    "created_at": "2026-02-02T17:30:00.000000",
    "started_at": "2026-02-02T17:30:05.000000",
    "completed_at": "2026-02-02T17:35:00.000000",
    "result": {
      "status": "success",
      "message": "All checks passed",
      "checks": [
        {
          "check_id": "completeness",
          "check_name_he": "בדיקת שלמות",
          "status": "pass",
          "findings_count": 0,
          "duration_ms": 1500
        },
        ...
      ],
      "output_file": "output/סיגמא/סיגמא_monthly_report.xlsx",
      "email_sent": true,
      "duration_seconds": 295.5
    }
  }
}
```

**Response (running):**
```json
{
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "progress": {
      "current_check": "unusual_assets",
      "checks_completed": 2,
      "checks_total": 7,
      "percent": 28,
      "message": "Running check: סוגי נכסים חריגים"
    }
  }
}
```

---

#### DELETE /api/jobs/{job_id}

Cancel a running job.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| job_id | path | Job UUID |

**Response:**
```json
{
  "success": true,
  "message": "Job cancelled"
}
```

---

### Managers

#### GET /api/managers

List all fund managers.

**Response:**
```json
{
  "managers": [
    {
      "key": "migdal",
      "id": "10040",
      "name_he": "מגדל",
      "name_en": "Migdal",
      "enabled": true
    },
    {
      "key": "ayalon",
      "id": "10054",
      "name_he": "איילון",
      "name_en": "Ayalon",
      "enabled": true
    },
    ...
  ]
}
```

---

#### GET /api/managers/{manager_key}

Get details of a specific manager.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| manager_key | path | Manager key (e.g., "migdal", "sigma") |

**Response:**
```json
{
  "manager": {
    "key": "sigma",
    "id": "10048",
    "name_he": "סיגמא",
    "name_en": "Sigma",
    "enabled": true
  }
}
```

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently no rate limiting is enforced. This may change in production.

---

## WebSocket / SSE (Future)

Real-time job progress updates will be available via Server-Sent Events:

```
GET /api/jobs/{job_id}/stream
```

This endpoint streams progress events as the job runs.

---

## Interactive Documentation

When running the API locally, interactive documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
