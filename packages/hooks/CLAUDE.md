# Package: mizrahi-hooks

Validation hook implementations for the Mizrahi Compliance Platform.

## Purpose

This package contains the business logic for compliance validation:
- Hook base class and registry
- Hook implementations (monthly_report, special_transactions)
- Individual check functions

## Directory Structure

```
src/mizrahi_hooks/
├── __init__.py          # Package exports
├── base.py              # BaseHook abstract class
├── registry.py          # Hook registration decorator
├── exceptions.py        # Custom exceptions
│
├── monthly_report/      # Hook #1
│   ├── __init__.py
│   ├── hook.py          # MonthlyReportHook class
│   └── checks/          # 7 validation checks
│       ├── completeness.py
│       ├── unusual_assets.py
│       ├── new_assets.py
│       ├── quantity_changes.py
│       ├── clause_328.py
│       ├── required_combinations.py
│       └── price_reasonableness.py
│
├── special_transactions/ # Hook #2
│   ├── __init__.py
│   ├── hook.py          # SpecialTransactionsHook class
│   └── checks/          # 7 validation checks
│       ├── duplicates.py
│       ├── dates.py
│       ├── decision_method.py
│       ├── sampling.py
│       ├── prices.py
│       └── problematic_securities.py
│
└── financial_report/    # Hook #3 (planned)
    └── __init__.py
```

## Hook Architecture

### Template Method Pattern

BaseHook.execute() defines the execution flow:
```python
async def execute(self, input_data: Dict[str, Any]) -> HookResult:
    # 1. Validate input
    is_valid, error = await self.validate_input(input_data)

    # 2. Fetch data from external sources
    data = await self.fetch_data(input_data)

    # 3. Run all validation checks
    check_results = await self.run_checks(data)

    # 4. Generate Excel report
    output_file = await self.generate_report(input_data, check_results)

    # 5. Send email notification
    await self._send_email(input_data, check_results, output_file)

    return HookResult(...)
```

### Creating a New Hook

1. Create directory: `src/mizrahi_hooks/<hook_name>/`
2. Create `hook.py` with class extending `BaseHook`
3. Register with `@register_hook("hook_id")` decorator
4. Implement abstract methods
5. Add configuration to `config/hooks.yaml`

```python
from mizrahi_hooks.base import BaseHook
from mizrahi_hooks.registry import register_hook

@register_hook("my_hook")
class MyHook(BaseHook):
    @property
    def hook_id(self) -> str:
        return "my_hook"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def checks(self) -> List[str]:
        return ["check_1", "check_2"]

    async def validate_input(self, input_data):
        # Validate input data
        return True, None

    async def fetch_data(self, input_data):
        # Fetch from Apify, load files, etc.
        return {}

    async def run_checks(self, data):
        # Execute validation checks
        return []

    async def generate_report(self, input_data, results):
        # Create Excel report
        return Path("report.xlsx")
```

### Creating a New Check

1. Create file in `checks/` directory
2. Define check function returning `CheckResult`
3. Add to hook's check list
4. Add configuration to `hooks.yaml`

```python
from mizrahi_shared.models import CheckResult

CHECK_ID = "my_check"
CHECK_NAME_HE = "בדיקה שלי"

async def check_my_check(data: Dict[str, Any]) -> CheckResult:
    start_time = time.time()
    findings = []

    # Validation logic here
    for item in data.get("items", []):
        if item_is_invalid(item):
            findings.append({
                "id": item["id"],
                "issue": "Description of issue",
            })

    return CheckResult(
        check_id=CHECK_ID,
        check_name=CHECK_ID,
        check_name_he=CHECK_NAME_HE,
        status="fail" if findings else "pass",
        message=f"Found {len(findings)} issues" if findings else "All valid",
        findings_count=len(findings),
        findings=findings,
        duration_ms=int((time.time() - start_time) * 1000),
    )
```

## Dependencies

- `mizrahi-shared` — Models, config, utilities
- `pandas` — Data processing
- `openpyxl` — Excel operations
- `selenium` — Browser automation (TASE scraping)
- `httpx` — HTTP client

## Testing

Compare output with legacy scripts:
```bash
# Run legacy script
python legacy/scripts/mizrahi_special_transactions.py --help

# Compare outputs
diff -r legacy_output/ new_output/
```

## Configuration

Hook behavior configured in `config/hooks.yaml`:
- Check enable/disable
- Parameters (thresholds, rules)
- Email settings
- Scheduling

Access via `self.get_parameter("key", default)` in hook code.

## Legacy Reference

Original implementations in `legacy/scripts/`:
- `fund_automation_complete.py` → monthly_report
- `mizrahi_special_transactions.py` → special_transactions

Use for debugging and verifying behavior matches.
