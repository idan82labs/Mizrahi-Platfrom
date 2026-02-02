# Package: mizrahi-shared

Shared utilities and models for the Mizrahi Compliance Platform.

## Purpose

This package provides common functionality used across the platform:
- Pydantic/dataclass models
- Configuration loading
- External service clients (Apify, Email)
- Excel report generation
- Logging utilities
- Constants and enumerations

## Directory Structure

```
src/mizrahi_shared/
├── __init__.py      # Package exports
├── models.py        # Data models (dataclasses)
├── config.py        # Configuration loader
├── apify.py         # Apify client for web scraping
├── email.py         # Email service (Resend)
├── excel.py         # Excel report generation
├── logging.py       # Structured logging
└── constants.py     # Constants and enums
```

## Models (models.py)

### Configuration Models
```python
@dataclass
class Manager:
    key: str
    id: str
    name_he: str
    name_en: str
    enabled: bool = True

@dataclass
class CheckConfig:
    id: str
    name_he: str
    description: str
    enabled: bool = True

@dataclass
class HookConfig:
    id: str
    name: str
    name_he: str
    # ... scheduling, parameters, checks
```

### Result Models
```python
@dataclass
class CheckResult:
    check_id: str
    check_name: str
    check_name_he: str
    status: str  # "pass" | "fail" | "warning" | "skipped"
    message: str
    findings_count: int = 0
    findings: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class HookResult:
    hook_id: str
    manager_name: str
    status: str  # "success" | "partial" | "failed"
    checks: List[CheckResult]
    output_file: Optional[Path] = None
    email_sent: bool = False
```

### Transaction Models
```python
@dataclass
class TransactionRow:
    # Fields from special transactions report
    fund_id: Optional[int]
    security_no: Optional[int]
    quantity: Optional[float]
    # ... etc

@dataclass
class PriceCheckResult:
    txn_id: str
    txn_price: float
    tase_price: Optional[float]
    variance_pct: Optional[float]
    status: str  # "pass" | "fail" | "no_data"
```

## Configuration (config.py)

Loads YAML configuration files:
```python
from mizrahi_shared.config import (
    get_hook_config,
    get_manager_by_name_he,
    get_all_managers,
)

# Get hook configuration
hook_config = get_hook_config("monthly_report")

# Get manager by Hebrew name
manager = get_manager_by_name_he("מגדל")
```

Configuration files:
- `config/hooks.yaml` — Hook definitions
- `config/managers.yaml` — Fund manager mappings

## Apify Client (apify.py)

Web scraping via Apify actors:
```python
from mizrahi_shared.apify import ApifyClient

async with ApifyClient() as client:
    # Run an actor
    run = await client.run_actor(
        actor_id="K9WppTziYC3n2vxTu",
        input_data={"param": "value"},
    )

    # Get results
    items = await client.get_dataset_items(run["defaultDatasetId"])
```

Actors used:
- `K9WppTziYC3n2vxTu` — Fetch mutual funds list
- `5lhI6O39Qbgv9O0gs` — Fetch manager reports

## Email Service (email.py)

Send emails via Resend:
```python
from mizrahi_shared.email import EmailService

email_service = EmailService()
success = await email_service.send_report(
    recipients=["user@example.com"],
    subject="Report Title",
    template="monthly_report",
    context={"manager_name": "מגדל"},
    attachment=Path("report.xlsx"),
)
```

## Excel Generation (excel.py)

Create formatted Excel reports:
```python
from mizrahi_shared.excel import generate_report

await generate_report(
    output_path=Path("output/report.xlsx"),
    hook_name="בדיקת דוחות חודשיים",
    manager_name="מגדל",
    check_results=[...],
    findings_by_check={...},
)
```

## Logging (logging.py)

Structured logging with context:
```python
from mizrahi_shared.logging import LogContext, log_check_start, log_check_end

with LogContext(hook_id="monthly_report", manager_name="מגדל"):
    log_check_start("completeness")
    # ... check logic
    log_check_end("completeness", status="pass")
```

## Constants (constants.py)

Shared constants and enumerations:
```python
from mizrahi_shared.constants import (
    UNUSUAL_ASSET_TYPES,
    REQUIRED_COMBINATIONS,
    JobStatus,
    TransactionType,
)
```

## Dependencies

- `pydantic` — Data validation
- `pyyaml` — YAML parsing
- `openpyxl` — Excel operations
- `httpx` — HTTP client
- `resend` — Email service

## Usage in Other Packages

```python
# In mizrahi-hooks
from mizrahi_shared.models import CheckResult, HookResult
from mizrahi_shared.config import get_hook_config
from mizrahi_shared.apify import ApifyClient

# In mizrahi-api
from mizrahi_shared.models import Manager, JobStatus
from mizrahi_shared.config import get_all_managers
```
