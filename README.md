# Mizrahi Compliance Platform - Legacy Hosting

> **IMPORTANT**: This is the `legacy/digitalocean-hosting` branch. It contains the standalone Digital Ocean deployment. **DO NOT merge this branch into `dev` or `main`**.

Regulatory compliance validation platform for Israeli mutual funds managed by Mizrahi Tefachot trustee.

## Branch Purpose

This branch maintains the **legacy standalone deployment** that runs on Digital Ocean. It includes:

- FastAPI server with both Hook 1 and Hook 2
- React frontend
- Standalone Python processing scripts
- No monorepo architecture dependencies

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+ (for frontend development)
- Apify API token
- Resend API key (optional, for email)

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
```

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
│       │   ├── mizrahi_special_transactions.py  # Hook 2 processor
│       │   ├── fund_automation_complete.py      # Hook 1 processor
│       │   └── batch_*.py
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

## API Endpoints

| Endpoint                      | Method | Description                   |
| ----------------------------- | ------ | ----------------------------- |
| `/`                           | GET    | Health check                  |
| `/api/managers`               | GET    | List fund managers            |
| `/api/process-report`         | POST   | Hook 2 - Special Transactions |
| `/api/process-monthly-report` | POST   | Hook 1 - Monthly Report       |
| `/api/job/{job_id}`           | GET    | Get job status                |
| `/api/download/{filename}`    | GET    | Download generated report     |

## Hooks

### Hook 1: Monthly Report Validation (Event ID: 5615)

Validates monthly fund holdings reports against Magna list.

**Checks:**

1. Completeness - Cross-reference Magna vs Manager reports
2. Unusual Assets - Flag unusual asset types
3. New Assets - New assets since previous month
4. Quantity Changes - Unusual changes month-over-month
5. Clause 328 - Borrowed quantity consistency
6. Required Combinations - Asset type combinations (Clause 214)
7. Price Reasonableness - Price ratio validation

### Hook 2: Special Transactions Validation (Event ID: 5618)

Validates coordinated and off-exchange trades.

**Checks:**

1. Inter-fund Transactions - Buy/sell pairs detection
2. Date Validation - Dates within report month
3. Decision Method - Decision method rules
4. דח"צ Voting - External director voting rules
5. Sampling - Random samples for verification
6. Price Checks - Price > 100 and internal comparison
7. Problematic Securities - Warning/halt/restricted lists

## Fund Managers

| Hebrew      | English          | ID    |
| ----------- | ---------------- | ----- |
| מגדל        | Migdal           | 10040 |
| איילון      | Ayalon           | 10054 |
| קסם         | Kesem            | 10047 |
| סיגמא       | Sigma            | 10048 |
| פורסט       | Forest           | 10082 |
| הראל        | Harel            | 10031 |
| אנליסט      | Analyst          | 10019 |
| מיטב        | Meitav           | 10083 |
| איביאי      | IBI              | 10068 |
| אלטשולר-שחם | Altshuler Shaham | 10017 |

## Environment Variables

| Variable          | Required | Description                                      |
| ----------------- | -------- | ------------------------------------------------ |
| `APIFY_API_TOKEN` | Yes      | Apify API token for data fetching                |
| `RESEND_API_KEY`  | No       | Resend API key for email sending                 |
| `OUTPUT_DIR`      | No       | Output directory (default: /tmp/mizrahi-outputs) |

## Testing

```bash
cd deploy/digitalocean

# Test Hook 2 offline (no Apify needed)
./test_offline_hook2.sh סיגמא

# Test Hook 1 (requires Apify token)
./test_hook1.sh סיגמא
```

## Documentation

See [docs/README.md](docs/README.md) for full documentation.

## License

Proprietary - 82Labs
