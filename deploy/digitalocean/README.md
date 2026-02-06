# Digital Ocean Unified Hosting

Unified hosting for all validation hooks on Digital Ocean server:

- **Hook 1**: Monthly Report Validation (Maya TASE Event 5618)
- **Hook 2**: Special Transactions Validation (Maya TASE Event 5615)
- **Hook 5**: K.303 Disclosure Validation (ISA Magna)

## Quick Start

```bash
# 1. Setup environment
cd deploy/digitalocean
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
cp config/credentials.env.example .env
nano .env  # Add your API keys

# 3. Run individual hooks
python scripts/batch_hook1_with_email.py --email "your@email.com"
python scripts/batch_hook2_with_email.py --email "your@email.com"
python scripts/batch_hook5_with_email.py --email "your@email.com"

# 4. Run all hooks for all managers
python scripts/batch_all_hooks.py --email "your@email.com" --send-email
```

## Directory Structure

```
/opt/mizrahi/
├── .env                                # Environment variables (gitignored)
├── requirements.txt                    # Python dependencies
├── server.py                           # Unified FastAPI server
├── scripts/
│   ├── hook_utils.py                   # Shared utilities (constants, Apify, email)
│   ├── fund_automation_complete.py     # Hook 1: Monthly Report processor
│   ├── mizrahi_special_transactions.py # Hook 2: Special Transactions processor
│   ├── mizrahi_4_logic.py              # Hook 4: Daily Tracking processor
│   ├── disclosure_k303_validator.py    # Hook 5: K.303 Disclosure processor
│   ├── batch_hook1_with_email.py       # Hook 1: Batch runner + email
│   ├── batch_hook2_with_email.py       # Hook 2: Batch runner + email
│   ├── batch_hook5_with_email.py       # Hook 5: Batch runner + email
│   └── batch_all_hooks.py             # Unified batch runner (all hooks)
├── config/
│   └── credentials.env.example         # Template for .env
├── test_data/                          # Test data for validation
├── output/                             # Generated reports (gitignored)
└── setup.sh                            # Initial setup script
```

## Email Configuration

All batch scripts use the Resend API for email delivery. The `--email` flag is
required and accepts comma-separated addresses:

```bash
python scripts/batch_hook1_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"
```

Environment variables are loaded from `.env` via `python-dotenv`.

## Hooks Overview

### Hook 1: Monthly Report Validation

- Validates monthly fund holdings reports
- Fetches data from Apify actors
- Generates Excel reports with findings

### Hook 2: Special Transactions Validation

- Validates coordinated/off-exchange trades
- Multiple validation checks (duplicates, dates, sampling, etc.)
- Generates Excel reports with sampled transactions

### Hook 5: K.303 Disclosure Validation

- Validates K.303 disclosure reports from ISA Magna
- Cross-references fund data against Mizrahi trustee list
- Checks include:
  - Fund completeness (1א)
  - Date validity (1ב)
  - Previous month comparison (2א)
  - Exposure profile validation (2ב)
  - Code combinations (3א-3ח)

## Running Individual Hooks

### Hook 1 (Monthly Report)

```bash
# All managers
python scripts/batch_hook1_with_email.py --email "your@email.com"

# Specific managers
python scripts/batch_hook1_with_email.py --managers "סיגמא,מגדל" --email "your@email.com"
```

### Hook 2 (Special Transactions)

```bash
# All managers
python scripts/batch_hook2_with_email.py --email "your@email.com"

# Specific managers with spec file
python scripts/batch_hook2_with_email.py --managers "מגדל,הראל" --email "your@email.com" --spec-file spec-file.xlsx
```

### Hook 5 (K.303 Disclosure)

```bash
# Test offline (no Apify needed, uses test data)
./test_offline_hook5.sh מגדל 2025-11

# Test via API (requires server running)
./test_hook5.sh מגדל test@test.com

# Direct script execution
python scripts/disclosure_k303_validator.py \
    --mutual-funds-list "Mutual_Funds_List.csv" \
    --current-report "current_month.csv" \
    --previous-report "previous_month.csv" \
    --output-xlsx "output.xlsx" \
    --report-month "2025-11" \
    --manager-name "מגדל"
```

## Testing

### Verify Output Matches Legacy

Test data is available in `test_data/` directory. Compare output:

```bash
# Run test for Hook 2
./test_hook2.sh

# Compare outputs
diff -r output/test_run/ test_data/expected_output/
```

## Troubleshooting

### Apify Token

Get your token from: https://console.apify.com/account/integrations

### Resend API Key

Get your key from: https://resend.com/api-keys

### Missing Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```
