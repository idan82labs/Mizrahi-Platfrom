# Legacy Code Reference

This directory contains the original implementation files from the pre-monorepo system.
These files are kept for reference and debugging purposes during the migration.

> **WARNING**: Do not modify these files. They are preserved for comparison with new implementations.

## Directory Structure

```
legacy/
├── scripts/          # Original Python scripts
├── workflows/        # n8n workflow definitions
└── docs/             # Original documentation
```

## Scripts

| File | Lines | Purpose |
|------|-------|---------|
| `fund_automation_complete.py` | ~984 | Hook #1: Monthly Report Validation |
| `mizrahi_special_transactions.py` | ~2,469 | Hook #2: Special Transactions Validation |
| `batch_special_transactions.py` | ~493 | Batch processing for all managers |
| `send_batch_email.py` | - | Email sender for batch results |
| `send_test_results.py` | - | Test results email |
| `test_special_transactions_all_managers.py` | - | Integration tests |
| `run_batch_all.sh` | - | Shell script to run batch for all managers |
| `run_batch_test.sh` | - | Shell script for test runs |

## Workflows

| File | Purpose |
|------|---------|
| `Funds Report Agent Processor.json` | n8n workflow for Hook #1 |
| `mizrahi_special_transactions_workflow.json` | n8n workflow for Hook #2 |

## Usage for Debugging

### Compare Output with New Implementation

```bash
# Run legacy script
cd legacy/scripts
python mizrahi_special_transactions.py \
    --manager-name "סיגמא" \
    --mutual-funds-list "path/to/list.xlsx" \
    --manager-report "path/to/report.csv" \
    --output-dir "./debug_output"

# Compare with new implementation output
diff -r ./debug_output ../output/
```

### Reference Original Logic

When implementing or debugging a check in the new system:

1. Find the corresponding function in the legacy script
2. Verify the logic matches
3. Compare output format and field names

### Key Functions Reference

**Hook #1 (fund_automation_complete.py):**
- Main validation logic
- Excel report generation
- Asset type checking rules

**Hook #2 (mizrahi_special_transactions.py):**
- `check_1_duplicates()` → `packages/hooks/.../checks/duplicates.py`
- `check_3_date_validation()` → `packages/hooks/.../checks/dates.py`
- `check_4_decision_method()` → `packages/hooks/.../checks/decision_method.py`
- `check_5_sampling()` → `packages/hooks/.../checks/sampling.py`
- `check_6_tase_prices()` → `packages/hooks/.../checks/prices.py`
- `check_7_problematic_securities()` → `packages/hooks/.../checks/problematic_securities.py`

## Original System Architecture

```
Original: n8n workflows → SSH → Python scripts → Gmail
New:      Web UI → FastAPI → Hook classes → Resend
```

## Configuration Reference

### Fund Managers (from legacy scripts)

```python
FUND_MANAGERS = {
    "מגדל": "10040",
    "איילון": "10054",
    "קסם": "10047",
    "סיגמא": "10048",
    "פורסט": "10082",
    "הראל": "10031",
    "אנליסט": "10019",
    "מיטב": "10083",
    "איביאי": "10068",
    "אלטשולר-שחם": "10017",
}
```

Now in: `config/managers.yaml`

### Apify Actor IDs

```python
FUNDS_LIST_ACTOR_ID = "K9WppTziYC3n2vxTu"
FUND_REPORTS_ACTOR_ID = "5lhI6O39Qbgv9O0gs"
```

Now in: `config/managers.yaml` under `apify:`

### Validation Rules

```python
# Unusual Asset Types (Hook #1)
UNUSUAL_ASSET_TYPES = [16, 21, 22, 23, 24, 52, 53, 57, 58, 99, 101, 112, 201, 207, 209]

# Required Combinations (Clause 214)
REQUIRED_COMBINATIONS = {
    111: [38, 42, 45, 47, 49, 56],
    212: [326, 327],
    213: [319],
    208: [307],
    210: [310],
}
```

Now in: `config/hooks.yaml` under each hook's `parameters:`

## Related Documentation

- [System Documentation](../docs/SYSTEM_DOCUMENTATION.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [Hooks Development](../docs/guides/HOOKS_DEVELOPMENT.md)
