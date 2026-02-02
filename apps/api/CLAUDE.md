# Backend: FastAPI + Python

This is the API server for the Mizrahi Compliance Platform.

## Tech Stack

- Python 3.11+
- FastAPI 0.109+
- Pydantic v2 for validation
- SQLModel for ORM (SQLAlchemy wrapper)
- Alembic for migrations
- APScheduler for task scheduling
- uv for package management

## Directory Structure

```
src/
├── main.py          # FastAPI app entry point
├── routers/         # API route handlers
│   ├── health.py    # Health check endpoint
│   ├── hooks.py     # Hook management
│   ├── jobs.py      # Job status tracking
│   └── managers.py  # Fund manager list
├── services/        # Business logic (planned)
├── workers/         # Background workers (planned)
├── scheduler/       # Task scheduling (planned)
└── db/
    └── migrations/  # Alembic migrations
```

## Commands

- `uv sync` — Install dependencies
- `uv run uvicorn src.main:app --reload` — Start dev server
- `uv run pytest` — Run tests
- `uv run ruff check .` — Lint code
- `uv run ruff format .` — Format code
- `uv run mypy .` — Type check

## Code Conventions

### Async/Await
- All I/O operations must be async
- Use `async def` for route handlers
- Use `await` for database queries and HTTP calls

### Type Hints
- Required on all function signatures
- Use Pydantic models for request/response schemas
- Use `Optional[T]` or `T | None` for nullable types

### Naming
- snake_case for functions and variables
- PascalCase for classes and Pydantic models
- UPPER_CASE for constants

### Imports
```python
# Standard library
from typing import Any, Dict, List, Optional

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Local
from .services import HookService
from mizrahi_shared.models import HookResult
```

### Error Handling
- Use HTTPException for API errors
- Include detail message for debugging
- Log errors with context

## API Structure

### Routers
| Prefix | Router | Purpose |
|--------|--------|---------|
| `/health` | health.py | Health checks |
| `/api/hooks` | hooks.py | Hook management |
| `/api/jobs` | jobs.py | Job tracking |
| `/api/managers` | managers.py | Manager list |

### Response Format
```python
{
    "data": {...},
    "error": None,
    "meta": {"timestamp": "...", "version": "1.0.0"}
}
```

## Dependencies

Local packages (editable installs via uv):
- `mizrahi-hooks` — Validation hook implementations
- `mizrahi-shared` — Shared utilities and models

## Database

### Development
- SQLite: `dev.db` in project root
- Async driver: `aiosqlite`

### Production
- PostgreSQL via `DATABASE_URL` env var
- Async driver: `asyncpg`
- Connection pooling configured

### Migrations
```bash
cd apps/api
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

## Configuration

Environment variables loaded from:
1. `.env` file (development)
2. System environment (production)

Key variables:
- `DATABASE_URL` — Database connection string
- `APIFY_API_TOKEN` — Apify API token
- `RESEND_API_KEY` — Email service API key
- `CORS_ORIGINS` — Allowed CORS origins

## Testing

- pytest with async support
- Test files in `tests/` directory
- Use `pytest-asyncio` for async tests
- Mock external services (Apify, Resend)

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_hooks.py

# Run with coverage
uv run pytest --cov=src
```

## Linting & Formatting

Using Ruff (replaces flake8, black, isort):

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

Configuration in `pyproject.toml`:
- Line length: 100
- Target: Python 3.11
- Rules: E, F, I, N, W, UP
