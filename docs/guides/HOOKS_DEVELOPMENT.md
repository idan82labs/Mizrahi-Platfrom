# Hooks Development Guide

This guide explains how to create and maintain validation hooks in the Mizrahi Compliance Platform.

---

## Overview

Hooks are self-contained validation modules that:
1. Fetch data from external sources (Apify, files, APIs)
2. Run a series of validation checks
3. Generate Excel reports with findings
4. Send email notifications

---

## Hook Architecture

```
packages/hooks/src/mizrahi_hooks/
├── __init__.py              # Package init, imports all hooks
├── base.py                  # BaseHook abstract class
├── registry.py              # Hook registration system
├── exceptions.py            # Custom exceptions
│
├── monthly_report/          # Hook #1
│   ├── __init__.py
│   ├── hook.py              # MonthlyReportHook class
│   └── checks/
│       ├── __init__.py
│       ├── completeness.py
│       ├── unusual_assets.py
│       └── ...
│
└── special_transactions/    # Hook #2
    ├── __init__.py
    ├── hook.py              # SpecialTransactionsHook class
    └── checks/
        ├── __init__.py
        ├── duplicates.py
        └── ...
```

---

## BaseHook Class

All hooks must extend `BaseHook` and implement these abstract methods:

```python
from mizrahi_hooks.base import BaseHook
from mizrahi_hooks.registry import register_hook

@register_hook("my_hook")
class MyHook(BaseHook):
    """My custom validation hook."""

    @property
    def hook_id(self) -> str:
        """Unique identifier - must match hooks.yaml key."""
        return "my_hook"

    @property
    def version(self) -> str:
        """Semantic version for tracking changes."""
        return "1.0.0"

    @property
    def checks(self) -> list[str]:
        """List of check IDs this hook performs."""
        return ["check_1", "check_2", "check_3"]

    async def validate_input(self, input_data: dict) -> tuple[bool, str | None]:
        """
        Validate input before processing.

        Returns:
            (True, None) if valid
            (False, "error message") if invalid
        """
        if not input_data.get("manager_name"):
            return False, "manager_name is required"
        return True, None

    async def fetch_data(self, input_data: dict) -> dict:
        """
        Fetch data from external sources.

        Args:
            input_data: Validated input (manager_name, email, etc.)

        Returns:
            Dictionary with data for checks to use
        """
        # Fetch from Apify, load files, call APIs, etc.
        return {
            "records": [...],
            "metadata": {...},
        }

    async def run_checks(self, data: dict) -> list[CheckResult]:
        """
        Execute validation checks.

        Args:
            data: Dictionary from fetch_data()

        Returns:
            List of CheckResult objects
        """
        results = []
        for check_func in [check_1, check_2, check_3]:
            result = await check_func(data)
            results.append(result)
        return results

    async def generate_report(
        self,
        input_data: dict,
        results: list[CheckResult],
    ) -> Path:
        """
        Generate Excel report.

        Returns:
            Path to generated .xlsx file
        """
        # Use ExcelGenerator from mizrahi_shared
        return Path("output/report.xlsx")
```

---

## Template Method Pattern

The `execute()` method in `BaseHook` implements the template method pattern:

```python
async def execute(self, input_data: dict) -> HookResult:
    """Don't override this - it orchestrates the hook execution."""

    # 1. Validate input
    valid, error = await self.validate_input(input_data)
    if not valid:
        return HookResult(status="failed", error=error, ...)

    # 2. Fetch data
    data = await self.fetch_data(input_data)

    # 3. Run checks
    results = await self.run_checks(data)

    # 4. Generate report
    output_file = await self.generate_report(input_data, results)

    # 5. Send email (if enabled)
    if self.config.email_enabled:
        await self._send_email(input_data, results, output_file)

    return HookResult(...)
```

---

## Creating a Check

### Check Function Structure

```python
# packages/hooks/src/mizrahi_hooks/my_hook/checks/my_check.py

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "my_check"
CHECK_NAME_HE = "הבדיקה שלי"


async def my_check(data: Dict[str, Any]) -> CheckResult:
    """
    Check description here.

    Args:
        data: Dictionary containing the data to validate

    Returns:
        CheckResult with findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        records = data.get("records", [])
        threshold = data.get("parameters", {}).get("threshold", 10)

        for record in records:
            # Validation logic
            if record.get("value") > threshold:
                findings.append({
                    "id": record.get("id"),
                    "value": record.get("value"),
                    "threshold": threshold,
                    "reason": "Value exceeds threshold",
                })

        # Determine status
        if findings:
            status = "fail"
            message = f"נמצאו {len(findings)} חריגות"
        else:
            status = "pass"
            message = "כל הערכים בסדר"

        logger.info(f"Check {CHECK_ID}: {len(findings)} findings")

        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status=status,
            message=message,
            findings_count=len(findings),
            findings=findings,
            duration_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.exception(f"Check {CHECK_ID} error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
```

### Check Status Values

| Status | Description | Excel Color |
|--------|-------------|-------------|
| `pass` | Check passed, no issues | Green |
| `fail` | Check found critical issues | Red |
| `warning` | Check found non-critical issues | Yellow |
| `skipped` | Check was disabled or skipped | Gray |

---

## Configuration

### Adding Hook to hooks.yaml

```yaml
# config/hooks.yaml

hooks:
  my_hook:
    id: "my_hook"
    name: "My Custom Hook"
    name_he: "הבדיקה המותאמת שלי"
    description: "Validates my custom data"
    status: "development"  # active | development | specification

    schedule:
      enabled: false
      cron: "0 9 5 * *"
      timezone: "Asia/Jerusalem"

    parameters:
      # Custom parameters accessible via self.get_parameter()
      threshold: 10
      sample_size: 5
      asset_types: [1, 2, 3, 4, 5]
      rules:
        required: [100, 200]
        optional: [300]

    checks:
      - id: "check_1"
        name_he: "בדיקה ראשונה"
        description: "First validation check"
        enabled: true

      - id: "check_2"
        name_he: "בדיקה שנייה"
        description: "Second validation check"
        enabled: true

      - id: "check_3"
        name_he: "בדיקה שלישית"
        description: "Third validation check"
        enabled: false  # Disabled by default

    email:
      enabled: true
      template: "my_hook"
      recipients_from_input: true
      cc:
        - "admin@82labs.io"

    output:
      format: "xlsx"
      include_review_columns: true
```

### Accessing Configuration in Hook

```python
class MyHook(BaseHook):
    async def run_checks(self, data: dict):
        # Get a parameter with default
        threshold = self.get_parameter("threshold", 10)

        # Check if a specific check is enabled
        if self.is_check_enabled("check_3"):
            results.append(await check_3(data))

        # Get check configuration
        check_config = self.get_check_config("check_1")
        # Returns: {"id": "check_1", "name_he": "בדיקה ראשונה", ...}
```

---

## Data Flow

```
Input Data                    Fetch Data                    Run Checks
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│ manager_name│              │ Apify API   │              │ Check 1     │
│ email       │──────────────│ File Load   │──────────────│ Check 2     │
│ parameters  │              │ HTTP APIs   │              │ Check 3     │
└─────────────┘              └─────────────┘              └─────────────┘
                                    │                            │
                                    ▼                            ▼
                             ┌─────────────┐              ┌─────────────┐
                             │ data dict:  │              │ results:    │
                             │ - records   │              │ - CheckResult│
                             │ - metadata  │              │ - CheckResult│
                             │ - params    │              │ - CheckResult│
                             └─────────────┘              └─────────────┘
                                                                 │
                                                                 ▼
                                                         ┌─────────────┐
                                                         │ Excel Report│
                                                         │ Email Send  │
                                                         └─────────────┘
```

---

## Using Shared Utilities

### Apify Client

```python
from mizrahi_shared.apify import ApifyClient, fetch_funds_list

async def fetch_data(self, input_data):
    async with ApifyClient() as client:
        # Run an actor
        result = await client.run_actor(
            "actor_id",
            input_data={"param": "value"},
        )

        # Get dataset items
        items = await client.get_dataset_items(
            result["defaultDatasetId"]
        )

    return {"items": items}
```

### Excel Generator

```python
from mizrahi_shared.excel import ExcelGenerator, generate_report

async def generate_report(self, input_data, results):
    # Simple approach
    return await generate_report(
        output_path=Path("output/report.xlsx"),
        hook_name=self.config.name_he,
        manager_name=input_data["manager_name"],
        check_results=[r.__dict__ for r in results],
        findings_by_check={r.check_id: r.findings for r in results},
    )

    # Or manual control
    generator = ExcelGenerator()
    generator.add_summary_sheet(
        hook_name=self.config.name_he,
        manager_name=input_data["manager_name"],
        check_results=[...],
    )
    generator.add_sheet("ממצאים", findings_data)
    return generator.save(Path("output/report.xlsx"))
```

### Email Service

```python
from mizrahi_shared.email import EmailService

async def send_custom_email(self):
    service = EmailService()
    await service.send_report(
        recipients=["user@example.com"],
        subject="דוח בדיקה",
        template="my_template",
        context={"key": "value"},
        attachment=Path("report.xlsx"),
    )
```

---

## Testing Hooks

### Unit Testing a Check

```python
import pytest
from mizrahi_hooks.my_hook.checks.my_check import my_check

@pytest.mark.asyncio
async def test_my_check_pass():
    data = {
        "records": [
            {"id": 1, "value": 5},
            {"id": 2, "value": 8},
        ],
        "parameters": {"threshold": 10},
    }

    result = await my_check(data)

    assert result.status == "pass"
    assert result.findings_count == 0

@pytest.mark.asyncio
async def test_my_check_fail():
    data = {
        "records": [
            {"id": 1, "value": 15},  # Exceeds threshold
        ],
        "parameters": {"threshold": 10},
    }

    result = await my_check(data)

    assert result.status == "fail"
    assert result.findings_count == 1
    assert result.findings[0]["id"] == 1
```

### Integration Testing a Hook

```python
import pytest
from mizrahi_hooks import get_hook
from mizrahi_shared.config import get_hook_config

@pytest.mark.asyncio
async def test_my_hook_execution():
    config = get_hook_config("my_hook")
    hook = get_hook("my_hook", config)

    result = await hook.execute({
        "manager_name": "Test Manager",
        "email": "test@test.com",
    })

    assert result.status in ("success", "partial")
    assert len(result.checks) > 0
```

---

## Best Practices

### Do's

✅ Use async/await for I/O operations
✅ Include Hebrew names for UI display
✅ Log meaningful messages for debugging
✅ Handle exceptions gracefully
✅ Return findings in a consistent structure
✅ Use configuration for thresholds and rules
✅ Track check duration for performance monitoring

### Don'ts

❌ Don't hardcode configuration values
❌ Don't override the `execute()` method
❌ Don't catch all exceptions silently
❌ Don't put business logic in the hook class itself (use check functions)
❌ Don't make synchronous blocking calls

---

## Debugging

### Using Legacy Files for Reference

When implementing or debugging a check, reference the original implementation:

```bash
# View original check implementation
grep -A 50 "def check_4" /home/alexandr/remote_backup/mizrahi_special_transactions.py

# Run original for comparison
cd /home/alexandr/remote_backup
python mizrahi_special_transactions.py --manager-name "סיגמא" --help
```

### Enabling Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or per-logger
logger = logging.getLogger("hook.my_hook")
logger.setLevel(logging.DEBUG)
```

### Testing with Mock Data

```python
# Create mock data matching expected structure
mock_data = {
    "transactions": [
        {
            "security_no": 12345,
            "quantity": 100,
            "price": 50.0,
            "transaction_date": "2026-01-15",
        }
    ],
    "parameters": {
        "threshold": 5.0,
    }
}

result = await my_check(mock_data)
print(result)
```

---

## Checklist for New Hook

- [ ] Create hook directory structure
- [ ] Implement hook class extending BaseHook
- [ ] Register hook with @register_hook decorator
- [ ] Implement all abstract methods
- [ ] Create check functions in checks/ subdirectory
- [ ] Add configuration to hooks.yaml
- [ ] Import hook in __init__.py
- [ ] Write unit tests for checks
- [ ] Write integration test for hook
- [ ] Update documentation
- [ ] Test with real data
