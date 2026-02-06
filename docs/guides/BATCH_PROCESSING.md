# Batch Processing Guide

**Last Updated**: 2026-02-06

## Overview

All batch processing uses dedicated Python scripts that:
1. Fetch data from Apify actors (Maya TASE / ISA Magna)
2. Run the processor script for each manager
3. Send branded HTML emails with Excel attachments via Resend API

### Batch Scripts

| Script                      | Hook | Description                    |
|-----------------------------|------|--------------------------------|
| `batch_hook1_with_email.py` | 1    | Monthly Report validation      |
| `batch_hook2_with_email.py` | 2    | Special Transactions validation|
| `batch_hook5_with_email.py` | 5    | K.303 Disclosure validation    |
| `batch_all_hooks.py`        | All  | Unified: Hook 1 + 2 + 5       |

All scripts import shared code from `hook_utils.py` (constants, Apify helpers,
email templates, logging).

---

## Prerequisites

### 1. Python Dependencies

```bash
cd deploy/digitalocean
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` from template:

```bash
cp config/credentials.env.example .env
nano .env  # Fill in your API keys
```

Required variables:

| Variable          | Required | Source                                      |
|-------------------|----------|---------------------------------------------|
| `APIFY_API_TOKEN` | Yes      | https://console.apify.com/account/integrations |
| `RESEND_API_KEY`  | Yes      | https://resend.com/api-keys                 |
| `FROM_EMAIL`      | No       | Default: noreply@notifications.82labs.io    |
| `TASE_API_KEY`    | No       | https://info.tase.co.il/en/datahub (Hook 4)|

---

## Running Batch Processing

### Individual Hooks

```bash
cd deploy/digitalocean

# Hook 1 - All 8 managers
python scripts/batch_hook1_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"

# Hook 2 - All 8 managers
python scripts/batch_hook2_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"

# Hook 5 - All 8 managers
python scripts/batch_hook5_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"
```

### Specific Managers

```bash
python scripts/batch_hook1_with_email.py --managers "מגדל,סיגמא" --email "your@email.com"
python scripts/batch_hook2_with_email.py --managers "מגדל,הראל" --email "your@email.com"
python scripts/batch_hook5_with_email.py --managers "מגדל" --email "your@email.com"
```

### All Hooks at Once

```bash
# Via unified batch script (sends consolidated email per manager)
python scripts/batch_all_hooks.py --email "your@email.com" --send-email

# Via shell script (runs each hook sequentially)
./run_all_managers.sh --email "your@email.com"
```

### Shell Script Runners

```bash
./run_hook1.sh --email "your@email.com"
./run_hook2.sh --email "your@email.com"
./run_hook5.sh --email "your@email.com"
./run_all_managers.sh --email "your@email.com"
```

---

## Command-Line Arguments

All batch scripts share a consistent CLI interface:

| Argument         | Required | Description                              |
|------------------|----------|------------------------------------------|
| `--email`        | Yes      | Comma-separated recipient email addresses|
| `--managers`     | No       | Comma-separated manager names (default: all 8) |
| `--output-dir`   | No       | Output directory (default: ./output/batch_hookN) |

Hook 2 additional options:

| Argument             | Description                              |
|----------------------|------------------------------------------|
| `--spec-file`        | Path to specification Excel file         |
| `--skip-tase-prices` | Skip TASE price checks (faster)          |

---

## Output Structure

Each batch run creates a timestamped directory:

```
output/batch_hook1/
└── 20260206_090000/
    ├── Mutual_Funds_List.xlsx
    ├── batch_summary.json
    ├── מגדל/
    │   ├── דוח_מגדל_2025-12.xlsx
    │   └── מגדל_email.json
    ├── סיגמא/
    │   └── ...
    └── ...
```

---

## Fund Managers (8)

| Name        | ID    |
|-------------|-------|
| מגדל        | 10040 |
| קסם         | 10047 |
| סיגמא       | 10048 |
| הראל        | 10031 |
| אנליסט      | 10019 |
| מיטב        | 10083 |
| איביאי      | 10068 |
| אלטשולר-שחם | 10017 |

---

## Testing

### Offline Tests (No Apify Needed)

```bash
# Hook 2 - uses local test data
./test_offline_hook2.sh סיגמא

# Hook 5 - uses local test data
./test_offline_hook5.sh מגדל 2025-11
```

### Live Tests (Requires Apify Token)

```bash
# Single manager test
./test_hook1.sh סיגמא
./test_hook2.sh סיגמא

# Unified batch test (single manager, no email)
./test_batch_all.sh "your@email.com" סיגמא
```

### Processing Time

- Per manager: ~2-5 minutes (depends on Apify actor speed)
- All 8 managers, all hooks: ~30-60 minutes
- With `--skip-tase-prices`: ~50% faster for Hook 2

---

## Troubleshooting

### "No report available" for a Manager

The Apify actor could not find a report on Maya for that manager/month.
This is normal if no report was filed yet.

### Email Not Received

1. Check `RESEND_API_KEY` is set in `.env`
2. Check sender email is verified in Resend dashboard
3. Check spam folder
4. Verify `--email` flag was provided

### Batch Processing Slow

- Use `--skip-tase-prices` for Hook 2
- Process specific managers with `--managers`
- Each hook has retry logic (3 attempts, 30s delay)

---

## Support

For issues or questions, contact: elay.g@82labs.io
