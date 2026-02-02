# Development Guide

This guide covers setting up the development environment and working with the Mizrahi Compliance Platform codebase.

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Node.js | 20+ | `nvm install 20` |
| pnpm | 9+ | `npm install -g pnpm` |
| Python | 3.11+ | System package manager |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | 2.x | System package manager |

### Optional Tools

| Tool | Purpose |
|------|---------|
| Docker | Containerized development |
| VS Code | Recommended IDE |
| Postman/Insomnia | API testing |

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/idan82labs/Mizrahi-Platfrom.git
cd Mizrahi-Platfrom
```

### 2. Install Node.js Dependencies

```bash
pnpm install
```

### 3. Install Python Dependencies

```bash
cd apps/api
uv sync
cd ../..
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required for data fetching
APIFY_API_TOKEN=your_apify_token

# Required for email sending
RESEND_API_KEY=your_resend_key

# Optional: Gmail for development
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

---

## Running the Application

### Development Mode

**Option 1: Using script**
```bash
./scripts/dev.sh
```

**Option 2: Manual startup**

Terminal 1 (Frontend):
```bash
pnpm dev:web
```

Terminal 2 (API):
```bash
pnpm dev:api
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Project Structure

```
mizrahi-compliance-platform/
├── apps/
│   ├── web/                 # React frontend
│   └── api/                 # FastAPI backend
├── packages/
│   ├── hooks/               # Validation hooks library
│   └── shared/              # Shared utilities
├── config/                  # YAML configuration
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

---

## Working with Hooks

### Creating a New Hook

1. **Create directory structure:**

```bash
mkdir -p packages/hooks/src/mizrahi_hooks/my_new_hook/checks
```

2. **Create hook class:**

```python
# packages/hooks/src/mizrahi_hooks/my_new_hook/hook.py

from mizrahi_hooks.base import BaseHook
from mizrahi_hooks.registry import register_hook

@register_hook("my_new_hook")
class MyNewHook(BaseHook):
    @property
    def hook_id(self) -> str:
        return "my_new_hook"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def checks(self) -> list[str]:
        return ["check_1", "check_2"]

    async def validate_input(self, input_data):
        # Validate input
        return True, None

    async def fetch_data(self, input_data):
        # Fetch required data
        return {}

    async def run_checks(self, data):
        # Run validation checks
        return []

    async def generate_report(self, input_data, results):
        # Generate Excel report
        return Path("report.xlsx")
```

3. **Create check implementations:**

```python
# packages/hooks/src/mizrahi_hooks/my_new_hook/checks/check_1.py

from mizrahi_shared.models import CheckResult

async def check_1(data: dict) -> CheckResult:
    findings = []
    # ... check logic ...

    return CheckResult(
        check_id="check_1",
        check_name="check_1",
        check_name_he="בדיקה 1",
        status="pass" if not findings else "fail",
        message="בדיקה עברה בהצלחה",
        findings=findings,
    )
```

4. **Add configuration:**

```yaml
# config/hooks.yaml

hooks:
  my_new_hook:
    id: "my_new_hook"
    name: "My New Hook"
    name_he: "הבדיקה החדשה שלי"
    status: "development"

    schedule:
      enabled: false
      cron: "0 9 1 * *"

    parameters:
      threshold: 10

    checks:
      - id: "check_1"
        name_he: "בדיקה 1"
        enabled: true
```

5. **Register hook:**

```python
# packages/hooks/src/mizrahi_hooks/__init__.py

from . import my_new_hook  # Add this line
```

---

## Working with Checks

### Check Structure

Each check is an async function that:
1. Receives data dictionary
2. Performs validation logic
3. Returns a `CheckResult`

```python
import time
from mizrahi_shared.models import CheckResult

async def check_example(data: dict) -> CheckResult:
    start_time = time.time()
    findings = []

    try:
        # Your validation logic here
        for item in data.get("items", []):
            if item.get("value") < 0:
                findings.append({
                    "item_id": item["id"],
                    "value": item["value"],
                    "reason": "Negative value"
                })

        # Determine status
        status = "pass" if not findings else "fail"
        message = "All items valid" if not findings else f"Found {len(findings)} issues"

        return CheckResult(
            check_id="example",
            check_name="example",
            check_name_he="בדיקת דוגמה",
            status=status,
            message=message,
            findings_count=len(findings),
            findings=findings,
            duration_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        return CheckResult(
            check_id="example",
            check_name="example",
            check_name_he="בדיקת דוגמה",
            status="fail",
            message=f"Error: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
```

---

## Testing

### Running Tests

```bash
# All tests
pnpm test

# Python tests only
pnpm test:py

# Frontend tests
pnpm --filter web test
```

### Testing a Hook Manually

```python
import asyncio
from mizrahi_hooks import get_hook
from mizrahi_shared.config import get_hook_config

async def test_hook():
    config = get_hook_config("monthly_report")
    hook = get_hook("monthly_report", config)

    result = await hook.execute({
        "manager_name": "סיגמא",
        "manager_id": "10048",
        "email": "test@example.com",
    })

    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    for check in result.checks:
        print(f"  {check.check_name_he}: {check.status}")

asyncio.run(test_hook())
```

---

## Configuration

### Hooks Configuration (hooks.yaml)

```yaml
hooks:
  hook_id:
    id: "hook_id"
    name: "Hook Name"
    name_he: "שם הבדיקה"
    status: "active"  # active | development | specification

    schedule:
      enabled: true
      cron: "0 9 5 * *"  # Cron expression
      timezone: "Asia/Jerusalem"

    parameters:
      # Hook-specific parameters
      threshold: 5.0
      list_param: [1, 2, 3]
      dict_param:
        key: value

    checks:
      - id: "check_id"
        name_he: "שם הבדיקה"
        enabled: true

    email:
      enabled: true
      template: "hook_template"
      cc:
        - "admin@example.com"
```

### Adding a New Manager

Edit `config/managers.yaml`:

```yaml
managers:
  new_manager:
    id: "12345"
    name_he: "שם חדש"
    name_en: "New Name"
    enabled: true
```

---

## Debugging

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
pnpm dev:api
```

### Check Legacy Implementation

For debugging, compare with the original working files:

```bash
# Reference the original implementation
cat /home/alexandr/remote_backup/mizrahi_special_transactions.py | grep "def check_4"

# Run original script for comparison
cd /home/alexandr/remote_backup
source mizrahi-venv/bin/activate
python mizrahi_special_transactions.py --help
```

See [Legacy Files Reference](../reference/LEGACY_FILES_REFERENCE.md) for more details.

### Common Issues

**Issue: Config not loading**
```bash
# Check CONFIG_DIR is set or run from project root
export CONFIG_DIR=/path/to/Mizrahi-Platfrom/config
```

**Issue: Import errors**
```bash
# Ensure packages are installed in development mode
cd apps/api && uv sync
```

**Issue: CORS errors**
```bash
# Add your frontend URL to CORS_ORIGINS
export CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Code Style

### Python

- Use `ruff` for linting
- Follow PEP 8
- Type hints required for public functions

```bash
# Lint Python code
pnpm lint:py

# Auto-fix issues
cd apps/api && uv run ruff check --fix .
```

### TypeScript

- Use ESLint configuration
- Follow existing code patterns

```bash
# Lint frontend
pnpm lint:web
```

---

## Git Workflow

### Branch Naming

```
feature/add-new-hook
fix/price-check-threshold
docs/update-api-reference
refactor/extract-email-service
```

### Commit Messages

Follow conventional commits:

```
feat(hooks): add financial report validation hook
fix(api): handle missing manager_id in job creation
docs(readme): update development setup instructions
refactor(shared): extract email templates to config
test(hooks): add unit tests for price check
```

### Pull Request Process

1. Create feature branch
2. Make changes
3. Run tests: `pnpm test`
4. Run linting: `pnpm lint`
5. Push and create PR
6. Request review

---

## Useful Commands

```bash
# Start development
./scripts/dev.sh

# Build frontend
pnpm build:web

# Run all linting
pnpm lint

# Clean node_modules
pnpm clean

# Check Python types
cd apps/api && uv run mypy src/

# Generate OpenAPI schema
curl http://localhost:8000/openapi.json > docs/api/openapi.json
```
