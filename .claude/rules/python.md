---
paths:
  - "deploy/digitalocean/**/*.py"
---

# Python Rules

Rules for Python code in the legacy deployment.

## Type Hints

- Recommended on function signatures
- Use `Optional[T]` or `T | None` for nullable types
- Use type aliases for complex types

```python
from typing import Any, Dict, List, Optional

def process_data(
    items: List[Dict[str, Any]],
    threshold: Optional[float] = None,
) -> Dict[str, int]:
    ...
```

## Async/Await

- Use `async def` for I/O operations in FastAPI server
- Database queries, HTTP calls, file operations should be async
- Use `asyncio.gather()` for parallel operations
- Standalone scripts may use synchronous code

```python
# FastAPI server - async preferred
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Standalone scripts - sync is OK
def fetch_data():
    response = requests.get(url)
    return response.json()
```

## Naming Conventions

- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- `_private` prefix for internal/private members

## Error Handling

- Use specific exceptions, not generic `Exception`
- Use FastAPI's `HTTPException` for API errors
- Include error context in exception messages
- Log errors with context for debugging

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
from fastapi import APIRouter
from pydantic import BaseModel

# 3. Local (relative)
from .utils import helper_function
```

## Testing

For standalone scripts, manual testing is acceptable:

```bash
cd deploy/digitalocean

# Test Hook 2 offline
./test_offline_hook2.sh סיגמא

# Test Hook 1 (requires Apify token)
./test_hook1.sh סיגמא
```

## Formatting

- Use consistent indentation (4 spaces)
- Line length: 100 characters recommended
- Keep scripts self-contained and readable
