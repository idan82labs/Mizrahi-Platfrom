# System Design

This document describes the high-level architecture, data flow, and directory
structure for the Mizrahi Compliance Platform.

**Related Documents:**

- [Overview](./OVERVIEW.md) - Goals and requirements
- [Hook System](./HOOK_SYSTEM.md) - Hook plugin architecture
- [Configuration](./CONFIGURATION.md) - YAML configuration format

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Data Flow](#data-flow)
3. [Directory Structure](#directory-structure)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MONOREPO                                        │
│                     mizrahi-compliance-platform/                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         apps/                                        │    │
│  │  ┌─────────────────────┐      ┌─────────────────────────────────┐   │    │
│  │  │  web/               │      │  api/                           │   │    │
│  │  │  (React + Vite)     │ ──── │  (FastAPI + Uvicorn)            │   │    │
│  │  │                     │ HTTP │                                  │   │    │
│  │  │  - Dashboard        │      │  - /api/hooks                   │   │    │
│  │  │  - Hook Runner      │      │  - /api/jobs                    │   │    │
│  │  │  - Job History      │      │  - /api/schedules               │   │    │
│  │  │  - Settings         │      │  - Background Workers           │   │    │
│  │  └─────────────────────┘      │  - Scheduler Engine             │   │    │
│  │                               └──────────────┬──────────────────┘   │    │
│  └──────────────────────────────────────────────┼──────────────────────┘    │
│                                                  │                           │
│  ┌──────────────────────────────────────────────┼──────────────────────┐    │
│  │                         packages/             │                      │    │
│  │  ┌─────────────────────┐      ┌──────────────▼──────────────────┐   │    │
│  │  │  shared/            │      │  hooks/                         │   │    │
│  │  │                     │      │                                  │   │    │
│  │  │  - config.py        │◄─────│  - base.py (BaseHook)           │   │    │
│  │  │  - models.py        │      │  - registry.py                  │   │    │
│  │  │  - apify.py         │      │  - monthly_report/              │   │    │
│  │  │  - email.py         │      │  - special_transactions/        │   │    │
│  │  │  - excel.py         │      │  - financial_report/ (future)   │   │    │
│  │  │  - logging.py       │      │                                  │   │    │
│  │  └─────────────────────┘      └──────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                         config/                                       │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐  │    │
│  │  │  hooks.yaml    │  │  managers.yaml │  │  environments/         │  │    │
│  │  │                │  │                │  │  ├── production.yaml   │  │    │
│  │  │  - schedules   │  │  - fund list   │  │  ├── staging.yaml     │  │    │
│  │  │  - parameters  │  │  - IDs         │  │  └── development.yaml │  │    │
│  │  │  - checks      │  │  - status      │  │                        │  │    │
│  │  └────────────────┘  └────────────────┘  └────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ External Services
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌───────────┐  │
│  │  Apify         │  │  TASE Maya     │  │  Resend        │  │ PostgreSQL│  │
│  │  (Scraping)    │  │  (Market Data) │  │  (Email)       │  │ (Jobs DB) │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
1. TRIGGER
   ├── Scheduled (APScheduler cron)
   ├── Manual (Frontend form submission)
   └── API (Direct POST to /api/hooks/{id}/run)
              │
              ▼
2. JOB CREATION
   └── Create Job record in PostgreSQL
       Status: "queued"
              │
              ▼
3. WORKER PICKUP
   └── Background worker picks up job
       Status: "running"
              │
              ▼
4. HOOK EXECUTION
   ├── Load hook from registry
   ├── Validate input
   ├── Fetch data (Apify actors)
   ├── Run checks (1-7)
   ├── Generate Excel report
   └── Send email notification
              │
              ▼
5. COMPLETION
   └── Update Job record
       Status: "completed" | "failed"
       Store: results, output path, duration
              │
              ▼
6. NOTIFICATION
   ├── Email to recipients
   ├── Slack webhook (optional)
   └── SSE to frontend (real-time)
```

---

## Directory Structure

```
mizrahi-compliance-platform/
│
├── package.json                    # Root workspace configuration
├── pnpm-workspace.yaml             # pnpm workspace definition
├── docker-compose.yml              # Local development + production
├── docker-compose.override.yml     # Local dev overrides
├── Dockerfile                      # Multi-stage production build
├── .env.example                    # Environment variables template
├── .gitignore
├── README.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint, test, type-check on PR
│       ├── deploy.yml              # Build & deploy on merge to main
│       └── release.yml             # Version tagging and changelog
│
├── apps/
│   │
│   ├── web/                        # React Frontend Application
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   ├── tailwind.config.ts
│   │   ├── index.html
│   │   ├── public/
│   │   │   └── favicon.ico
│   │   └── src/
│   │       ├── main.tsx            # Application entry point
│   │       ├── App.tsx             # Router configuration
│   │       ├── pages/
│   │       │   ├── Dashboard.tsx       # Overview of all hooks
│   │       │   ├── HookRunner.tsx      # Generic hook execution UI
│   │       │   ├── HookDetails.tsx     # Hook-specific information
│   │       │   ├── JobHistory.tsx      # Past runs and results
│   │       │   ├── JobDetail.tsx       # Single job details
│   │       │   ├── Settings.tsx        # Schedule configuration
│   │       │   └── NotFound.tsx        # 404 page
│   │       ├── components/
│   │       │   ├── layout/
│   │       │   │   ├── TopBar.tsx
│   │       │   │   ├── Sidebar.tsx
│   │       │   │   └── Footer.tsx
│   │       │   ├── hooks/
│   │       │   │   ├── HookCard.tsx
│   │       │   │   ├── HookForm.tsx
│   │       │   │   ├── CheckTable.tsx
│   │       │   │   └── StatusBadge.tsx
│   │       │   ├── jobs/
│   │       │   │   ├── JobList.tsx
│   │       │   │   ├── JobProgress.tsx
│   │       │   │   └── JobResultCard.tsx
│   │       │   └── ui/             # shadcn/ui components
│   │       │       └── ... (button, card, dialog, etc.)
│   │       ├── api/
│   │       │   ├── client.ts       # API client configuration
│   │       │   ├── hooks.ts        # Hook-related API calls
│   │       │   ├── jobs.ts         # Job-related API calls
│   │       │   └── types.ts        # TypeScript interfaces
│   │       ├── hooks/              # React hooks
│   │       │   ├── useJobStream.ts # SSE subscription
│   │       │   ├── useHooks.ts     # TanStack Query hooks
│   │       │   └── useToast.ts
│   │       ├── lib/
│   │       │   └── utils.ts        # Utility functions
│   │       └── assets/
│   │           ├── logo.svg
│   │           └── images/
│   │
│   └── api/                        # FastAPI Backend Application
│       ├── pyproject.toml          # Python dependencies (uv/poetry)
│       ├── uv.lock                 # Lock file
│       ├── alembic.ini             # Database migrations config
│       └── src/
│           ├── __init__.py
│           ├── main.py             # FastAPI application entry
│           ├── config.py           # Settings management (pydantic)
│           ├── dependencies.py     # FastAPI dependencies
│           │
│           ├── routers/
│           │   ├── __init__.py
│           │   ├── hooks.py        # /api/hooks endpoints
│           │   ├── jobs.py         # /api/jobs endpoints
│           │   ├── schedules.py    # /api/schedules endpoints
│           │   ├── managers.py     # /api/managers endpoints
│           │   └── health.py       # /health endpoints
│           │
│           ├── services/
│           │   ├── __init__.py
│           │   ├── hook_runner.py  # Hook execution logic
│           │   ├── job_service.py  # Job CRUD operations
│           │   └── email_service.py# Email sending
│           │
│           ├── scheduler/
│           │   ├── __init__.py
│           │   ├── engine.py       # APScheduler setup
│           │   └── loader.py       # Load schedules from config
│           │
│           ├── workers/
│           │   ├── __init__.py
│           │   └── processor.py    # Background job processor
│           │
│           ├── db/
│           │   ├── __init__.py
│           │   ├── database.py     # Database connection
│           │   ├── models.py       # SQLModel/SQLAlchemy models
│           │   └── migrations/     # Alembic migrations
│           │       ├── env.py
│           │       └── versions/
│           │
│           └── tests/
│               ├── conftest.py
│               ├── test_hooks.py
│               ├── test_jobs.py
│               └── test_schedules.py
│
├── packages/
│   │
│   ├── hooks/                      # Core Hooks Library (Python)
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── mizrahi_hooks/
│   │           ├── __init__.py
│   │           ├── base.py         # BaseHook abstract class
│   │           ├── registry.py     # Hook discovery & registration
│   │           ├── exceptions.py   # Custom exceptions
│   │           │
│   │           ├── monthly_report/         # Hook #1
│   │           │   ├── __init__.py
│   │           │   ├── hook.py             # MonthlyReportHook class
│   │           │   ├── config.py           # Hook-specific config
│   │           │   └── checks/
│   │           │       ├── __init__.py
│   │           │       ├── completeness.py
│   │           │       ├── unusual_assets.py
│   │           │       ├── new_assets.py
│   │           │       ├── quantity_changes.py
│   │           │       ├── clause_328.py
│   │           │       ├── required_combinations.py
│   │           │       └── price_reasonableness.py
│   │           │
│   │           ├── special_transactions/   # Hook #2
│   │           │   ├── __init__.py
│   │           │   ├── hook.py             # SpecialTransactionsHook class
│   │           │   ├── config.py
│   │           │   └── checks/
│   │           │       ├── __init__.py
│   │           │       ├── chk1_duplicates.py
│   │           │       ├── chk3_dates.py
│   │           │       ├── chk4_decision.py
│   │           │       ├── chk5_sampling.py
│   │           │       ├── chk6_prices.py
│   │           │       └── chk7_problematic.py
│   │           │
│   │           └── financial_report/       # Hook #3 (Future)
│   │               ├── __init__.py
│   │               └── hook.py             # Stub
│   │
│   ├── shared/                     # Shared Python Utilities
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── mizrahi_shared/
│   │           ├── __init__.py
│   │           ├── config.py       # Load YAML configs
│   │           ├── constants.py    # FUND_MANAGERS, etc. (loaded from YAML)
│   │           ├── models.py       # Shared dataclasses
│   │           ├── apify.py        # Apify client wrapper
│   │           ├── email.py        # Email service abstraction
│   │           ├── excel.py        # Excel generation utilities
│   │           ├── logging.py      # Structured logging setup
│   │           └── rate_limit.py   # Rate limiting utilities
│   │
│   └── ui/                         # Shared React Components (Optional)
│       ├── package.json
│       └── src/
│           ├── index.ts
│           ├── CheckTable.tsx
│           ├── StatusBadge.tsx
│           └── HookCard.tsx
│
├── config/
│   ├── hooks.yaml                  # Hook definitions & schedules
│   ├── managers.yaml               # Fund manager configuration
│   ├── email.yaml                  # Email templates & settings
│   └── environments/
│       ├── production.yaml         # Production-specific config
│       ├── staging.yaml            # Staging-specific config
│       └── development.yaml        # Development-specific config
│
├── scripts/
│   ├── dev.sh                      # Start local development
│   ├── build.sh                    # Build all packages
│   ├── test.sh                     # Run all tests
│   ├── migrate.sh                  # Run database migrations
│   ├── seed.sh                     # Seed test data
│   └── deploy.sh                   # Manual deployment script
│
└── docs/
    ├── README.md                   # Documentation index
    ├── architecture/               # Architecture documents (this directory)
    └── guides/                     # Development guides
```

---

**Next:** [Hook System](./HOOK_SYSTEM.md)
