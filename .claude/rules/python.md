---
paths:
  - "apps/api/**/*.py"
  - "packages/**/*.py"
---

# Python Rules

Rules for Python code in the backend and packages.

## Type Hints

- Required on all function signatures
- Use `Optional[T]` or `T | None` for nullable types
- Use type aliases for complex types
- Import types from `typing` module

```python
from typing import Any, Dict, List, Optional

def process_data(
    items: List[Dict[str, Any]],
    threshold: Optional[float] = None,
) -> Dict[str, int]:
    ...
```

## Async/Await

- Use `async def` for all I/O operations
- Database queries, HTTP calls, file operations must be async
- Use `asyncio.gather()` for parallel operations
- Never use blocking calls in async functions

```python
# Correct
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Incorrect - blocking
def fetch_data():
    response = requests.get(url)  # Blocks event loop!
```

## Naming Conventions

- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- `_private` prefix for internal/private members

## Pydantic Models

- Use for all API request/response schemas
- Use for configuration validation
- Use `Field()` for validation and metadata
- Use `model_validator` for complex validation

```python
from pydantic import BaseModel, Field, model_validator

class HookRequest(BaseModel):
    manager_name: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    @model_validator(mode='after')
    def validate_manager(self) -> 'HookRequest':
        # Custom validation
        return self
```

## Error Handling

- Use specific exceptions, not generic `Exception`
- Create custom exceptions in `exceptions.py`
- Use FastAPI's `HTTPException` for API errors
- Include error context in exception messages

```python
from fastapi import HTTPException, status

if not manager:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Manager not found: {manager_name}"
    )
```

## Imports

```python
# 1. Standard library
import asyncio
from pathlib import Path
from typing import Any, Dict, List

# 2. Third-party
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 3. Local - absolute
from mizrahi_shared.models import HookResult
from mizrahi_hooks.base import BaseHook

# 4. Local - relative (same package only)
from .services import HookService
```

## Dataclasses vs Pydantic

- **Dataclasses**: Internal data structures, no validation needed
- **Pydantic**: API schemas, configuration, external data

## Testing

- Use pytest with pytest-asyncio
- Test files in `tests/` directory
- Use fixtures for common setup
- Mock external services (Apify, Resend)

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_apify_client():
    client = AsyncMock()
    client.run_actor.return_value = {"defaultDatasetId": "test-id"}
    return client

@pytest.mark.asyncio
async def test_fetch_data(mock_apify_client):
    result = await fetch_data(mock_apify_client)
    assert result is not None
```

## Formatting

- Use Ruff for formatting and linting
- Line length: 100 characters
- Use `ruff format .` before committing
