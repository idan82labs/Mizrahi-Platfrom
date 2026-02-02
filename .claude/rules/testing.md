# Testing Rules

Guidelines for testing across the codebase.

## Test Requirements by Change Type

### Major Changes (Run Full Suite + New Tests)
- Features affecting multiple modules
- Database schema changes
- API endpoint changes
- Configuration file changes
- Changes to shared packages

### Minor Changes (Targeted Tests + New Tests)
- Single-module features
- Bug fixes in isolated code
- UI component updates
- Utility function changes

### No Tests Required
- Documentation-only changes
- Comment updates
- README updates

## Test Structure

### Arrange-Act-Assert Pattern
```python
def test_validate_manager():
    # Arrange
    input_data = {"manager_name": "מגדל", "email": "test@test.com"}

    # Act
    result = validate_manager(input_data)

    # Assert
    assert result.is_valid
    assert result.error is None
```

### Descriptive Names
- Format: `test_<function>_<condition>_<expected>`
- Examples:
  - `test_validate_input_with_missing_email_returns_error`
  - `test_fetch_data_with_invalid_manager_raises_not_found`
  - `test_completeness_check_with_missing_funds_fails`

## What to Test

### DO Test
- Public API functions
- Business logic (validation checks)
- Error handling paths
- Edge cases (empty, null, boundary values)
- Integration between components

### DON'T Test
- Private/internal functions directly
- Third-party library behavior
- Implementation details
- Trivial getters/setters

## Mocking

### Mock at Boundaries Only
- External APIs (Apify, Resend)
- Database
- File system
- Network calls

### Don't Mock
- Internal modules
- Utility functions
- Data transformations

```python
# Good - mocking external service
@pytest.fixture
def mock_apify():
    with patch('mizrahi_shared.apify.ApifyClient') as mock:
        yield mock

# Bad - mocking internal function
@pytest.fixture
def mock_validate():  # Don't do this
    with patch('mizrahi_hooks.monthly_report.validate_input') as mock:
        yield mock
```

## Test Data

### Use Fixtures
```python
@pytest.fixture
def sample_manager():
    return Manager(
        key="migdal",
        id="10040",
        name_he="מגדל",
        name_en="Migdal",
    )

@pytest.fixture
def sample_hook_config():
    return HookConfig(
        id="monthly_report",
        name="Monthly Report",
        # ...
    )
```

### Factory Functions for Complex Data
```python
def create_transaction(**overrides) -> TransactionRow:
    defaults = {
        "row_index": 1,
        "fund_id": 12345,
        "security_no": 100,
        "quantity": 1000.0,
        "price": 10.50,
    }
    return TransactionRow(**{**defaults, **overrides})
```

## Coverage Requirements

- New code must have tests
- Aim for 80%+ coverage on changed files
- Critical paths (validation logic) should have 100% coverage

## TypeScript Errors

**All TypeScript errors must be fixed before commit.**

Run type checking:
```bash
pnpm typecheck
```

## Running Tests

### Python
```bash
# All tests
cd apps/api && uv run pytest

# Specific file
cd apps/api && uv run pytest tests/test_hooks.py

# Specific test
cd apps/api && uv run pytest tests/test_hooks.py::test_validate_input

# With coverage
cd apps/api && uv run pytest --cov=src --cov-report=html
```

### TypeScript (planned)
```bash
# All tests
pnpm test

# Specific file
pnpm test -- tests/Component.test.tsx
```

## CI/CD Integration

Tests run automatically on:
- Pull request creation
- Push to `dev` branch
- Before merge to `main`

Failing tests block the merge.
