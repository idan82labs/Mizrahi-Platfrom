# Digital Ocean Unified Hosting

Unified hosting for all validation hooks on Digital Ocean server:

- **Hook 1**: Monthly Report Validation (Maya TASE Event 5618)
- **Hook 2**: Special Transactions Validation (Maya TASE Event 5615)
- **Hook 5**: K.303 Disclosure Validation (ISA Magna)

## Quick Start

```bash
# 1. Copy files to server
scp -r deploy/digitalocean/* root@209.38.226.220:/opt/mizrahi/

# 2. SSH to server
ssh root@209.38.226.220

# 3. Setup environment
cd /opt/mizrahi
./setup.sh

# 4. Configure credentials
cp config/credentials.env.example config/credentials.env
nano config/credentials.env  # Add your API keys

# 5. Run hooks
./run_hook1.sh             # Monthly Report (single manager)
./run_hook2.sh             # Special Transactions (single manager)
./run_all_managers.sh      # Both hooks for all managers
```

## Directory Structure

```
/opt/mizrahi/
├── scripts/
│   ├── fund_automation_complete.py     # Hook 1: Monthly Report
│   ├── mizrahi_special_transactions.py # Hook 2: Special Transactions
│   ├── disclosure_k303_validator.py    # Hook 5: K.303 Disclosure
│   ├── batch_special_transactions.py   # Hook 2: Batch processor
│   ├── batch_monthly_report.py         # Hook 1: Batch processor
│   └── send_email.py                   # Email utility
├── config/
│   ├── credentials.env.example
│   └── credentials.env                 # Your API keys (gitignored)
├── test_data/
│   └── hook5/                          # K.303 test data
├── output/                             # Generated reports
├── logs/                               # Execution logs
├── run_hook1.sh                        # Run Hook 1
├── run_hook2.sh                        # Run Hook 2
├── test_offline_hook5.sh               # Test Hook 5 offline
├── test_hook5.sh                       # Test Hook 5 via API
├── run_all_managers.sh                 # Run all hooks for all managers
└── setup.sh                            # Initial setup script
```

## Email Configuration

**Test Email:** `alexandrf539@gmail.com`

All scripts are configured to send results to this test email. To change, edit
the `EMAIL_RECIPIENT` variable in:

- `scripts/batch_monthly_report.py`
- `scripts/batch_special_transactions.py`

Or use the `--email` command line argument.

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
# Single manager
./run_hook1.sh --fund-name "סיגמא"

# With email
./run_hook1.sh --fund-name "סיגמא" --send-email

# All managers
python scripts/batch_monthly_report.py --send-email
```

### Hook 2 (Special Transactions)

```bash
# Single manager
./run_hook2.sh --manager "סיגמא"

# All managers
python scripts/batch_special_transactions.py --apify-token $APIFY_TOKEN

# With email
python scripts/batch_special_transactions.py --apify-token $APIFY_TOKEN --send-email
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

### Gmail App Password

1. Enable 2-factor authentication on Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an App Password for "Mail"
4. Use this password (not your regular password)

### Apify Token

Get your token from: https://console.apify.com/account/integrations

### Missing Dependencies

```bash
source /opt/mizrahi/venv/bin/activate
pip install pandas openpyxl requests
```
