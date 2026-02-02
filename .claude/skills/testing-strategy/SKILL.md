---
name: testing-strategy
description: |
  Testing strategy for Mizrahi project. Use when implementing features or fixes
  to determine what tests to run and write. Distinguishes between major and minor
  changes with different test requirements.
allowed-tools: Bash, Read, Grep, Glob
---

# Testing Strategy Skill

Determines appropriate testing scope based on change type.

## Change Classification

### Major Changes
Changes that might affect other parts of the application:
- Database schema changes
- API endpoint modifications
- Shared utility changes
- Configuration changes
- Hook logic modifications
- Changes to `packages/shared/`
- Changes affecting multiple modules

**Requirements:**
- Run FULL test suite
- Write new tests for new functionality
- Verify no regressions

### Minor Changes
Isolated changes with limited scope:
- Single-file bug fixes
- UI component updates
- Adding individual checks
- Utility function additions
- Styling changes

**Requirements:**
- Run TARGETED tests (related to change)
- Write tests for new functionality
- No need for full suite

### No Tests Required
- Documentation-only changes (`.md` files)
- Comment updates
- README changes

**Note:** Config changes (`.yaml`, `.json`) DO require tests.

## Decision Flow

```
Is it a documentation-only change?
├── Yes → No tests required
└── No → Continue...

Does it modify multiple modules or shared code?
├── Yes → MAJOR: Run full suite + new tests
└── No → Continue...

Does it change database schema or API contracts?
├── Yes → MAJOR: Run full suite + new tests
└── No → Continue...

Does it modify configuration files?
├── Yes → MAJOR: Run full suite
└── No → MINOR: Run targeted tests + new tests
```

## Running Tests

### Full Test Suite (Major Changes)
```bash
# Python tests
cd apps/api && uv run pytest

# TypeScript type checking
pnpm typecheck

# Linting
pnpm lint
```

### Targeted Tests (Minor Changes)
```bash
# Specific test file
cd apps/api && uv run pytest tests/test_specific.py

# Tests matching pattern
cd apps/api && uv run pytest -k "test_completeness"

# Tests for a module
cd apps/api && uv run pytest tests/hooks/
```

## Writing New Tests

### For New Hook Check
```python
# tests/hooks/test_monthly_report/test_new_check.py
import pytest
from mizrahi_hooks.monthly_report.checks.new_check import check_new_check

@pytest.mark.asyncio
async def test_new_check_with_valid_data():
    data = {"items": [...]}
    result = await check_new_check(data)
    assert result.status == "pass"

@pytest.mark.asyncio
async def test_new_check_with_invalid_data():
    data = {"items": [...]}
    result = await check_new_check(data)
    assert result.status == "fail"
    assert result.findings_count > 0
```

### For API Endpoint
```python
# tests/api/test_hooks_router.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_hooks(client: AsyncClient):
    response = await client.get("/api/hooks")
    assert response.status_code == 200
    assert "data" in response.json()
```

## Pre-Commit Checklist

Before committing:

1. **TypeScript errors = 0**
   ```bash
   pnpm typecheck
   ```

2. **Linting passes**
   ```bash
   pnpm lint
   pnpm lint:py
   ```

3. **Tests pass** (based on change type)
   ```bash
   # Major
   pnpm test

   # Minor
   cd apps/api && uv run pytest tests/path/to/relevant/
   ```

4. **New tests written** for new functionality

## Coverage Goals

- New code: Must have tests
- Changed files: 80%+ coverage
- Critical paths (validation logic): 100% coverage
