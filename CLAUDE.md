# Project: Mizrahi Compliance Platform - Legacy Hosting

> **BRANCH WARNING**: This is the `legacy/digitalocean-hosting` branch.
> **DO NOT merge this branch into `dev` or `main`**.
> This branch is maintained separately for standalone Digital Ocean deployment.

Regulatory compliance validation platform for Israeli mutual funds managed by
Mizrahi Tefachot trustee. Automates validation of monthly reports and special
transactions against regulatory requirements.

## Tech Stack

### Frontend (frontend/)

- React 18.3 + TypeScript 5.8
- Vite 5.4 (build tool)
- TailwindCSS 3.4 + shadcn/ui (Radix primitives)
- React Query (data fetching)
- React Hook Form + Zod (forms/validation)
- Recharts (visualizations)

### Backend (deploy/digitalocean/)

- Python 3.11+
- FastAPI (unified server)
- Standalone Python scripts for hook processing
- Apify for web scraping (TASE Maya)
- Resend for email notifications (optional)

## Project Structure

```
mizrahi-compliance-platform/
├── frontend/                   # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
│
├── deploy/
│   └── digitalocean/          # Main deployment code
│       ├── server.py          # Unified FastAPI server
│       ├── scripts/
│       │   ├── hook_utils.py                    # Shared utilities module
│       │   ├── fund_automation_complete.py      # Hook 1 processor
│       │   ├── mizrahi_special_transactions.py  # Hook 2 processor
│       │   ├── mizrahi_4_logic.py               # Hook 4 processor
│       │   ├── disclosure_k303_validator.py     # Hook 5 processor
│       │   ├── batch_hook1_with_email.py        # Hook 1 batch runner
│       │   ├── batch_hook2_with_email.py        # Hook 2 batch runner
│       │   ├── batch_hook5_with_email.py        # Hook 5 batch runner
│       │   └── batch_all_hooks.py               # Unified batch runner
│       ├── test_data/         # Test data for validation
│       ├── config/            # Local config
│       └── README.md
│
├── config/                    # YAML configuration
│   ├── hooks.yaml            # Hook definitions
│   └── managers.yaml         # Fund manager mappings
│
├── docs/                      # Documentation
│
├── .claude/                   # Claude Code configuration
│
└── README.md                  # This file
```

## Commands

### Server Deployment (Digital Ocean)

```bash
cd deploy/digitalocean

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APIFY_API_TOKEN="your_token"
export RESEND_API_KEY="your_key"  # Optional

# Run server
python server.py
# Server runs on http://0.0.0.0:8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:5173

# Build for production
npm run build
```

### Testing Hooks

```bash
cd deploy/digitalocean

# Test Hook 2 offline (no Apify needed)
./test_offline_hook2.sh סיגמא

# Test Hook 1 (requires Apify token)
./test_hook1.sh סיגמא

# Test Hook 5 offline (K.303 disclosure, no Apify needed)
./test_offline_hook5.sh מגדל 2025-11

# Test Hook 5 via API (requires Apify token)
./test_hook5.sh מגדל test@test.com
```

## API Endpoints

| Endpoint                         | Method | Description                   |
| -------------------------------- | ------ | ----------------------------- |
| `/`                              | GET    | Health check                  |
| `/api/managers`                  | GET    | List fund managers            |
| `/api/process-report`            | POST   | Hook 2 - Special Transactions |
| `/api/process-monthly-report`    | POST   | Hook 1 - Monthly Report       |
| `/api/process-disclosure-report` | POST   | Hook 5 - K.303 Disclosure     |
| `/api/job/{job_id}`              | GET    | Get job status                |
| `/api/download/{filename}`       | GET    | Download generated report     |

## Hooks

### Hook 1: Monthly Report Validation (Event ID: 5618)

Validates monthly fund holdings reports against Magna list.

**Checks:**

1. Completeness - Cross-reference Magna vs Manager reports
2. Unusual Assets - Flag unusual asset types
3. New Assets - New assets since previous month
4. Quantity Changes - Unusual changes month-over-month
5. Clause 328 - Borrowed quantity consistency
6. Required Combinations - Asset type combinations (Clause 214)
7. Price Reasonableness - Price ratio validation

### Hook 2: Special Transactions Validation (Event ID: 5615)

Validates coordinated and off-exchange trades.

**Checks:**

1. Inter-fund Transactions - Buy/sell pairs detection
2. Date Validation - Dates within report month
3. Decision Method - Decision method rules
4. דח״צ Voting - External director voting rules
5. Sampling - Random samples for verification
6. Price Checks - Price > 100 and internal comparison
7. Problematic Securities - Warning/halt/restricted lists

### Hook 4: Daily Tracking (TASE Data Hub)

Validates daily fund tracking data against TASE market data.

**Checks:**

1. NAV tracking against benchmark index
2. BFIX/Bloomberg exchange rate validation
3. Management fee calculation verification
4. Index tracking accuracy (INDX)

### Hook 5: K.303 Disclosure Validation (ISA Magna)

Validates K.303 disclosure reports from ISA Magna.

**Checks:**

1. Check 1א - Fund Completeness: Cross-reference Magna vs disclosure report
2. Check 1ב - Date Validity: Report dates match expected month
3. Check 2א - Previous Month Comparison: Detect significant changes (>10%)
4. Check 2ב - Exposure Profile: Validate against fund's exposure profile
5. Checks 3א-3ח - Code Combinations: Cross-reference disclosure codes
   - 3א: FX exposure codes (0102/0302/0502 vs 06)
   - 3ב: Bond exposure codes (03 vs 07/08)
   - 3ג-3ח: Government/corporate bond code pairs

## Code Conventions

### General

- Use early returns over deep nesting
- Functions do one thing - if name has "and", split it
- No magic numbers - use named constants
- Group imports: stdlib → external → internal → types

### TypeScript (Frontend)

- Prefer named exports over default exports
- Use `@/` path alias for imports from src/
- Components in PascalCase, hooks use `use` prefix

### Python (Backend)

- Async functions for I/O operations
- Type hints on function signatures
- Keep scripts standalone and self-contained

### Hebrew Content

- Hebrew names allowed in user-facing output (UI, reports, emails)
- Internal code uses English identifiers
- Config files use Hebrew for display names (`name_he`)

## Git Workflow

### CRITICAL: Branch Rules

> **This branch (`legacy/digitalocean-hosting`) must NEVER be merged into `dev` or `main`.**
> It is maintained as a standalone legacy deployment.

### For This Branch Only

- Make fixes and updates directly on this branch
- Keep changes isolated from the main development workflow
- Document any significant changes in the README

## Security

### Critical (Compliance Platform)

- Never log fund data, transaction details, or PII
- Never expose validation rules in error messages
- All input validation happens server-side

### General

- Never hardcode secrets — use environment variables
- Never commit .env, credentials, or API keys
- Validate all user input

## Environment Variables

| Variable          | Required | Description                                      |
| ----------------- | -------- | ------------------------------------------------ |
| `APIFY_API_TOKEN` | Yes      | Apify API token for data fetching                |
| `RESEND_API_KEY`  | Yes      | Resend API key for email delivery                |
| `FROM_EMAIL`      | No       | Sender email (default: noreply@notifications.82labs.io) |
| `TASE_API_KEY`    | No       | TASE Data Hub API key (for Hook 4 index data)    |

## Domain Context

### Fund Managers (8 configured)

מגדל, קסם, סיגמא, הראל, אנליסט, מיטב, איביאי, אלטשולר-שחם

### Maya TASE Event IDs

- **5618** — Monthly Report (Hook 1)
- **5615** — Special Transactions (Hook 2)

### ISA Magna

- **K.303** — Disclosure Reports (Hook 5) — from magna.isa.gov.il

### Configuration Files

- `config/hooks.yaml` — Hook definitions, checks, parameters
- `config/managers.yaml` — Fund manager mappings, Apify config

## Documentation

- @docs/README.md — Documentation index
- @docs/guides/SYSTEM_GUIDE.md — System operations guide
- @docs/guides/BATCH_PROCESSING.md — Batch processing guide
- @deploy/digitalocean/README.md — Deployment documentation
