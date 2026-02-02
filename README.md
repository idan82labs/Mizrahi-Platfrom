# Mizrahi Compliance Platform

Regulatory compliance validation platform for Israeli mutual funds managed by Mizrahi Tefachot trustee.

## Overview

This monorepo contains all components of the Mizrahi Compliance Platform:

- **apps/web** - React frontend application
- **apps/api** - FastAPI backend API
- **packages/hooks** - Validation hooks library
- **packages/shared** - Shared utilities and models

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- pnpm 9+
- uv (Python package manager)

### Installation

```bash
# Clone repository
git clone https://github.com/idan82labs/Mizrahi-Platfrom.git
cd Mizrahi-Platfrom

# Install Node.js dependencies
pnpm install

# Install Python dependencies
cd apps/api && uv sync && cd ../..

# Copy environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Development

```bash
# Start frontend development server
pnpm dev:web

# Start API development server (in another terminal)
pnpm dev:api

# Or run both in parallel
pnpm dev
```

### Build

```bash
# Build frontend
pnpm build:web

# Lint code
pnpm lint
```

## Project Structure

```
mizrahi-compliance-platform/
├── apps/
│   ├── web/                    # React frontend
│   │   ├── src/
│   │   │   ├── pages/         # Page components
│   │   │   ├── components/    # UI components
│   │   │   └── api/           # API client
│   │   └── package.json
│   │
│   └── api/                    # FastAPI backend
│       ├── src/
│       │   ├── routers/       # API endpoints
│       │   ├── services/      # Business logic
│       │   └── db/            # Database models
│       └── pyproject.toml
│
├── packages/
│   ├── hooks/                  # Validation hooks
│   │   └── src/mizrahi_hooks/
│   │       ├── base.py        # BaseHook class
│   │       ├── registry.py    # Hook registry
│   │       ├── monthly_report/
│   │       └── special_transactions/
│   │
│   └── shared/                 # Shared utilities
│       └── src/mizrahi_shared/
│           ├── config.py      # Configuration loader
│           ├── models.py      # Data models
│           ├── apify.py       # Apify client
│           ├── email.py       # Email service
│           └── excel.py       # Excel utilities
│
├── config/
│   ├── hooks.yaml             # Hook definitions
│   ├── managers.yaml          # Fund managers
│   └── environments/          # Environment configs
│
└── scripts/                    # Utility scripts
```

## Hooks

### Hook #1: Monthly Report Validation

- **Status**: Active
- **Schedule**: 5th of every month at 09:00
- **Checks**:
  1. Completeness - Cross-reference Magna vs Manager reports
  2. Unusual Assets - Flag unusual asset types
  3. New Assets - Detect new assets since previous month
  4. Quantity Changes - Identify unusual quantity changes
  5. Clause 328 - Borrowed quantity consistency
  6. Required Combinations - Asset type combination rules
  7. Price Reasonableness - Price ratio validation

### Hook #2: Special Transactions Validation

- **Status**: Development
- **Schedule**: Manual trigger
- **Checks**:
  1. Duplicates - Inter-fund transactions
  2. Dates - Transaction dates within report month
  3. Decision Method - Decision method and דחצ voting rules
  4. Sampling - Random samples for verification
  5. Prices - Cross-check with TASE market data
  6. Problematic Securities - Warning/halt/restricted lists

## Configuration

Configuration is managed through YAML files in the `config/` directory:

- `hooks.yaml` - Hook definitions, schedules, and parameters
- `managers.yaml` - Fund manager definitions
- `environments/*.yaml` - Environment-specific settings

## API Endpoints

```
GET  /health                    # Health check
GET  /api/hooks                 # List all hooks
GET  /api/hooks/{hook_id}       # Get hook details
POST /api/hooks/{hook_id}/run   # Run a hook
GET  /api/jobs                  # List jobs
GET  /api/jobs/{job_id}         # Get job status
GET  /api/managers              # List managers
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `APIFY_API_TOKEN` | Apify API token for web scraping |
| `RESEND_API_KEY` | Resend API key for email |
| `DATABASE_URL` | Database connection string |
| `CORS_ORIGINS` | Allowed CORS origins |

## License

Proprietary - 82Labs
