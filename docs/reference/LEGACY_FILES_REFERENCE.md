# Legacy Files Reference

This document provides references to the original working files preserved in the repository.
Use these files for debugging individual hook workflows and understanding the original implementation.

**Legacy Location**: `./legacy/` (in repository root)

> **Note**: Legacy files were moved from external backup to the repository for portability.
> All developers now have access to the same reference files.

---

## Quick Reference

| New Location | Legacy File | Purpose |
|--------------|-------------|---------|
| `packages/hooks/src/mizrahi_hooks/monthly_report/` | `legacy/scripts/fund_automation_complete.py` | Hook #1 original implementation |
| `packages/hooks/src/mizrahi_hooks/special_transactions/` | `legacy/scripts/mizrahi_special_transactions.py` | Hook #2 original implementation |
| `config/hooks.yaml` | Various hardcoded configs | Hook configuration |
| `config/managers.yaml` | `FUND_MANAGERS` dict | Fund manager mapping |

---

## Python Scripts (Original Implementations)

### Hook #1: Monthly Report Validation

```
File: legacy/scripts/fund_automation_complete.py
Lines: ~984
Status: Production (Active)
```

**Key Functions to Reference:**
- Main validation logic
- Excel report generation
- Email formatting
- Asset type checking rules

**Run Standalone:**
```bash
cd legacy/scripts
python fund_automation_complete.py --help
```

---

### Hook #2: Special Transactions Validation

```
File: legacy/scripts/mizrahi_special_transactions.py
Lines: ~2,469
Status: Development
```

**Key Functions to Reference:**
- `check_1_duplicates()` → `packages/hooks/.../checks/duplicates.py`
- `check_3_date_validation()` → `packages/hooks/.../checks/dates.py`
- `check_4_decision_method()` → `packages/hooks/.../checks/decision_method.py`
- `check_5_sampling()` → `packages/hooks/.../checks/sampling.py`
- `check_6_tase_prices()` → `packages/hooks/.../checks/prices.py`
- `check_7_problematic_securities()` → `packages/hooks/.../checks/problematic_securities.py`

**Run Standalone:**
```bash
cd legacy/scripts

# Single manager test
python mizrahi_special_transactions.py \
    --manager-name "סיגמא" \
    --mutual-funds-list "path/to/Mutual_Funds_List.xlsx" \
    --manager-report "path/to/report.csv" \
    --output-dir "./output" \
    --emails "test@example.com"
```

---

### Batch Processing

```
File: legacy/scripts/batch_special_transactions.py
Lines: ~493
Status: Production
```

**Run Batch for All Managers:**
```bash
cd legacy/scripts
./run_batch_all.sh YOUR_APIFY_TOKEN [GMAIL_USER] [GMAIL_PASSWORD]
```

**Run Single Manager Test:**
```bash
./run_batch_test.sh YOUR_APIFY_TOKEN
```

---

## n8n Workflows (Original Orchestration)

### Hook #1 Workflow

```
File: legacy/workflows/Funds Report Agent Processor.json
n8n URL: https://n8n.82labs.io
Form: /form/fund-form
```

**Workflow Nodes:**
1. Schedule Trigger (5th of month @ 09:00)
2. Apify: Fetch Mutual Funds List
3. Apify: Fetch Manager Reports
4. Python: Run validation checks
5. Gmail: Send report email

**Import to n8n:**
```bash
# Copy workflow JSON to n8n import
cat "legacy/workflows/Funds Report Agent Processor.json" | pbcopy
# Then paste in n8n UI → Workflows → Import from JSON
```

---

### Hook #2 Workflow

```
File: legacy/workflows/mizrahi_special_transactions_workflow.json
n8n URL: https://n8n.82labs.io
Form: /form/mizrahi-special-transactions
```

**Workflow Nodes:**
1. Form Trigger (manual upload)
2. Extract Form Data
3. SSH: Create directories
4. SSH: Upload files (parallel)
5. SSH: Run Python script
6. SSH: Get output files
7. Gmail: Send report

---

## Email Scripts

### Batch Email Sender

```
File: legacy/scripts/send_batch_email.py
```

**Usage:**
```bash
python legacy/scripts/send_batch_email.py \
    --batch-dir "./batch_output/20260117_184128" \
    --gmail-user "your@gmail.com" \
    --gmail-password "app-password" \
    --recipients "recipient@example.com"
```

### Test Results Email

```
File: legacy/scripts/send_test_results.py
```

---

## Configuration Reference

### Fund Managers (Original Hardcoded)

```python
# From mizrahi_special_transactions.py
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

**New Location:** `config/managers.yaml`

---

### Apify Actor IDs

```python
# From original scripts
FUNDS_LIST_ACTOR_ID = "K9WppTziYC3n2vxTu"
FUND_REPORTS_ACTOR_ID = "5lhI6O39Qbgv9O0gs"
```

**New Location:** `config/managers.yaml` under `apify:`

---

### Validation Rules (Original)

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

# Decision Method Rules (Hook #2)
TYPE_REQUIRES_DECISION_1 = {12, 22}
TYPE_REQUIRES_DECISION_1_OR_2 = {31, 32, 33, 34, 35, 36}
```

**New Location:** `config/hooks.yaml` under each hook's `parameters:`

---

## Debugging Workflow

### Step 1: Test Original Script

```bash
cd legacy/scripts

# For Hook #2 with test data
python mizrahi_special_transactions.py \
    --manager-name "סיגמא" \
    --mutual-funds-list "path/to/Mutual_Funds_List.xlsx" \
    --manager-report "path/to/report.csv" \
    --output-dir "./debug_output" \
    --emails "test@test.com" \
    --skip-tase-prices
```

### Step 2: Compare Output

```bash
# Compare original output with new implementation
diff -r ./debug_output ../output/
```

---

## Version Comparison

| File | Lines | Notes |
|------|-------|-------|
| `mizrahi_special_transactions.py` | 2,469 | Has דחצ voting checks |
| `batch_special_transactions.py` | 493 | Event ID 5618 (correct) |
| `fund_automation_complete.py` | 984 | Complete implementation |

---

## API Keys & Credentials

**DO NOT commit these. Reference only.**

```
Apify Token: Set in APIFY_API_TOKEN environment variable
Resend API: Set in RESEND_API_KEY environment variable
Gmail: Use App Password with 2FA enabled
```

See `.env.example` in monorepo root for required variables.

---

## Server Deployment Reference

### Production Server

```
IP: 209.38.226.220
Domain: 209.38.226.220.nip.io
Deployment: /opt/mizrahi/
Dev workspace: /root/
Venv: /root/mizrahi-venv/
```

### Systemd Service

```bash
sudo systemctl status mizrahi-api
sudo systemctl restart mizrahi-api
sudo journalctl -u mizrahi-api -f
```

---

## Related Documentation

- [Legacy README](../../legacy/README.md) - Overview of legacy files
- [System Documentation](../SYSTEM_DOCUMENTATION.md) - Complete system overview
- [Architecture Plan](../ARCHITECTURE.md) - Monorepo architecture
- [System Guide](../guides/SYSTEM_GUIDE.md) - Original system guide
- [Batch Processing](../guides/BATCH_PROCESSING.md) - Batch processing guide
- [Cheatsheet](../CHEATSHEET.md) - Quick commands reference
