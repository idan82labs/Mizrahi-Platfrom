# Mizrahi Compliance Platform - Monorepo Architecture Plan

**Document Version**: 1.0
**Created**: 2026-02-02
**Status**: Planning Phase

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Requirements](#3-requirements)
4. [Proposed Architecture](#4-proposed-architecture)
5. [Directory Structure](#5-directory-structure)
6. [Hook Plugin System](#6-hook-plugin-system)
7. [Configuration Format](#7-configuration-format)
8. [API Design](#8-api-design)
9. [Hosting Recommendations](#9-hosting-recommendations)
10. [Additional Requirements](#10-additional-requirements)
11. [Migration Plan](#11-migration-plan)
12. [Technical Decisions](#12-technical-decisions)

---

## 1. Executive Summary

### Goal

Transform the current scattered Mizrahi Fund Automation System into a unified **monorepo** with:
- Single codebase for all components
- Plugin-based hook architecture for easy extensibility
- Unified hosting platform
- Configuration-driven schedules and parameters

### Key Outcomes

| Outcome | Description |
|---------|-------------|
| **Centralized Development** | All code in one repository with shared tooling |
| **Simplified Operations** | Single deployment target instead of 3 separate systems |
| **Extensible Architecture** | Add new hooks by creating a directory and registering |
| **Configuration-Driven** | Change schedules and parameters without code changes |
| **Audit Trail** | Full job history with database persistence |

---

## 2. Current State Analysis

### Current Architecture Problems

| Component | Current State | Problem |
|-----------|---------------|---------|
| **Code Location** | Files scattered across multiple directories | Duplicate code in 6+ places, version confusion |
| **Frontend** | Vercel (mizrahi-smart-tools-portal.vercel.app) | Separate deployment, links to n8n forms |
| **Backend** | VPS at 209.38.226.220 | Manual deployment, no CI/CD |
| **Orchestration** | n8n at n8n.82labs.io | Third system to maintain, workflow changes require n8n access |
| **Configuration** | Hardcoded in Python scripts | Changes require code deployment |
| **Job History** | None | No audit trail, no debugging history |

### Code Duplication Found

The following code is duplicated across 6+ files:

```python
# Found in: mizrahi_special_transactions.py, batch_special_transactions.py,
#           fund_automation_complete.py, test_special_transactions_all_managers.py,
#           and more...
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
    "אלטשולר-שחם": "10017"
}
```

### Current File Statistics

| Metric | Value |
|--------|-------|
| Total Python files | 14 |
| Total Frontend files | 70+ |
| Lines in mizrahi_special_transactions.py | 2,469 |
| Lines in fund_automation_complete.py | 984 |
| Lines in batch_special_transactions.py | 493 |
| Duplicated constant definitions | 6 places |

---

## 3. Requirements

### Primary Requirements (User-Specified)

| ID | Requirement | Priority |
|----|-------------|----------|
| R1 | Centralized repository for easy change tracking and debugging | High |
| R2 | Single hosting service to simplify maintenance | High |
| R3 | Frontend for manual hook triggering and intermediate data access | High |
| R4 | Easy implementation of new hooks into existing workflow | High |
| R5 | Configurable schedules with proper config format | High |

### Derived Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R6 | Job history and audit logging | Compliance, debugging |
| R7 | Real-time progress updates | UX improvement |
| R8 | Environment-based configuration | Dev/staging/prod separation |
| R9 | Health checks and monitoring | Operational visibility |
| R10 | Rate limiting for external services | Prevent API abuse |
| R11 | Comprehensive test infrastructure | Quality assurance |
| R12 | Notification system (email + Slack) | Team awareness |

---

## 4. Proposed Architecture

### High-Level Architecture

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

### Data Flow

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

## 5. Directory Structure

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
    ├── ARCHITECTURE.md             # This document
    ├── DEVELOPMENT.md              # Development setup guide
    ├── DEPLOYMENT.md               # Deployment procedures
    ├── API.md                      # API documentation
    └── HOOKS.md                    # Hook development guide
```

---

## 6. Hook Plugin System

### BaseHook Abstract Class

```python
# packages/hooks/src/mizrahi_hooks/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from pathlib import Path
from datetime import datetime
import time
import logging

@dataclass
class HookConfig:
    """Configuration loaded from hooks.yaml"""
    id: str
    name: str
    name_he: str
    description: str
    status: str  # "active" | "development" | "specification"
    schedule_enabled: bool
    schedule_cron: Optional[str]
    schedule_timezone: str
    parameters: Dict[str, Any]
    checks: List[Dict[str, Any]]
    email_enabled: bool
    email_template: str
    email_cc: List[str] = field(default_factory=list)

@dataclass
class CheckResult:
    """Result of a single validation check"""
    check_id: str
    check_name: str
    check_name_he: str
    status: str  # "pass" | "fail" | "warning" | "skipped"
    message: str
    findings_count: int
    findings: List[Dict[str, Any]]
    duration_ms: int

@dataclass
class HookResult:
    """Result of complete hook execution"""
    hook_id: str
    manager_name: str
    manager_id: str
    status: str  # "success" | "partial" | "failed"
    message: str
    checks: List[CheckResult]
    output_file: Optional[Path]
    email_sent: bool
    email_recipients: List[str]
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    error: Optional[str] = None

class BaseHook(ABC):
    """
    Abstract base class for all validation hooks.

    To create a new hook:
    1. Create a new directory under packages/hooks/src/mizrahi_hooks/
    2. Implement a class that extends BaseHook
    3. Register the hook in registry.py
    4. Add configuration to config/hooks.yaml
    """

    def __init__(self, config: HookConfig):
        self.config = config
        self.logger = logging.getLogger(f"hook.{self.hook_id}")

    @property
    @abstractmethod
    def hook_id(self) -> str:
        """Unique identifier for the hook (e.g., 'monthly_report')"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Hook version (e.g., '1.0.0')"""
        pass

    @property
    @abstractmethod
    def checks(self) -> List[str]:
        """List of check IDs this hook performs"""
        pass

    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input before processing.

        Args:
            input_data: Dictionary with manager_name, email, etc.

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch required data from external sources.

        Args:
            input_data: Validated input data

        Returns:
            Dictionary with fetched data (dataframes, files, etc.)
        """
        pass

    @abstractmethod
    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute all validation checks.

        Args:
            data: Data returned from fetch_data()

        Returns:
            List of CheckResult objects
        """
        pass

    @abstractmethod
    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult]
    ) -> Path:
        """
        Generate Excel report with findings.

        Args:
            input_data: Original input data
            results: List of check results

        Returns:
            Path to generated Excel file
        """
        pass

    async def execute(self, input_data: Dict[str, Any]) -> HookResult:
        """
        Main execution flow - template method pattern.

        This method orchestrates the entire hook execution:
        1. Validate input
        2. Fetch data
        3. Run checks
        4. Generate report
        5. Send email

        Subclasses should NOT override this method.
        """
        started_at = datetime.utcnow()
        start_time = time.time()

        manager_name = input_data.get("manager_name", "Unknown")
        manager_id = input_data.get("manager_id", "")

        try:
            # Step 1: Validate input
            self.logger.info(f"Validating input for {manager_name}")
            is_valid, error = await self.validate_input(input_data)
            if not is_valid:
                return HookResult(
                    hook_id=self.hook_id,
                    manager_name=manager_name,
                    manager_id=manager_id,
                    status="failed",
                    message=f"Validation failed: {error}",
                    checks=[],
                    output_file=None,
                    email_sent=False,
                    email_recipients=[],
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                    duration_seconds=time.time() - start_time,
                    error=error
                )

            # Step 2: Fetch data
            self.logger.info(f"Fetching data for {manager_name}")
            data = await self.fetch_data(input_data)

            # Step 3: Run checks
            self.logger.info(f"Running {len(self.checks)} checks for {manager_name}")
            check_results = await self.run_checks(data)

            # Step 4: Generate report
            self.logger.info(f"Generating report for {manager_name}")
            output_file = await self.generate_report(input_data, check_results)

            # Step 5: Send email
            email_sent = False
            email_recipients = []
            if self.config.email_enabled:
                self.logger.info(f"Sending email for {manager_name}")
                email_sent, email_recipients = await self._send_email(
                    input_data, check_results, output_file
                )

            # Determine overall status
            failed_checks = [c for c in check_results if c.status == "fail"]
            warning_checks = [c for c in check_results if c.status == "warning"]

            if failed_checks:
                status = "partial"
                message = f"{len(failed_checks)} checks failed"
            elif warning_checks:
                status = "success"
                message = f"Completed with {len(warning_checks)} warnings"
            else:
                status = "success"
                message = "All checks passed"

            return HookResult(
                hook_id=self.hook_id,
                manager_name=manager_name,
                manager_id=manager_id,
                status=status,
                message=message,
                checks=check_results,
                output_file=output_file,
                email_sent=email_sent,
                email_recipients=email_recipients,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=time.time() - start_time
            )

        except Exception as e:
            self.logger.exception(f"Hook execution failed: {e}")
            return HookResult(
                hook_id=self.hook_id,
                manager_name=manager_name,
                manager_id=manager_id,
                status="failed",
                message=str(e),
                checks=[],
                output_file=None,
                email_sent=False,
                email_recipients=[],
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    async def _send_email(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult],
        output_file: Path
    ) -> tuple[bool, List[str]]:
        """Send email notification with report attachment."""
        from mizrahi_shared.email import EmailService

        email_service = EmailService()
        recipients = self._parse_recipients(input_data.get("email", ""))
        recipients.extend(self.config.email_cc)

        success = await email_service.send_report(
            template=self.config.email_template,
            recipients=recipients,
            subject=self._build_email_subject(input_data),
            context={
                "manager_name": input_data.get("manager_name"),
                "hook_name": self.config.name_he,
                "results": results,
                "timestamp": datetime.now().isoformat()
            },
            attachment=output_file
        )

        return success, recipients if success else []

    def _parse_recipients(self, email_str: str) -> List[str]:
        """Parse semicolon or comma separated email string."""
        if not email_str:
            return []
        separators = [";", ","]
        for sep in separators:
            if sep in email_str:
                return [e.strip() for e in email_str.split(sep) if e.strip()]
        return [email_str.strip()] if email_str.strip() else []

    def _build_email_subject(self, input_data: Dict[str, Any]) -> str:
        """Build email subject line."""
        manager = input_data.get("manager_name", "")
        return f"{self.config.name_he} - {manager}"
```

### Hook Registry

```python
# packages/hooks/src/mizrahi_hooks/registry.py

from typing import Dict, Type, Optional
from .base import BaseHook, HookConfig

# Registry of all available hooks
_HOOK_REGISTRY: Dict[str, Type[BaseHook]] = {}

def register_hook(hook_id: str):
    """Decorator to register a hook class."""
    def decorator(cls: Type[BaseHook]):
        _HOOK_REGISTRY[hook_id] = cls
        return cls
    return decorator

def get_hook(hook_id: str, config: HookConfig) -> Optional[BaseHook]:
    """Get an instance of a hook by ID."""
    hook_class = _HOOK_REGISTRY.get(hook_id)
    if hook_class is None:
        return None
    return hook_class(config)

def list_hooks() -> list[str]:
    """List all registered hook IDs."""
    return list(_HOOK_REGISTRY.keys())

# Auto-import all hooks to trigger registration
from .monthly_report import MonthlyReportHook
from .special_transactions import SpecialTransactionsHook
```

### Example Hook Implementation

```python
# packages/hooks/src/mizrahi_hooks/special_transactions/hook.py

from typing import Any, Dict, List, Optional
from pathlib import Path

from mizrahi_hooks.base import BaseHook, HookConfig, CheckResult
from mizrahi_hooks.registry import register_hook
from mizrahi_shared.apify import ApifyClient
from mizrahi_shared.excel import ExcelGenerator

from .checks import (
    check_duplicates,
    check_dates,
    check_decision_method,
    check_sampling,
    check_prices,
    check_problematic_securities
)

@register_hook("special_transactions")
class SpecialTransactionsHook(BaseHook):
    """
    Hook #2: Special Transactions Validation

    Validates coordinated/off-exchange trades including:
    - Inter-fund transactions (duplicates)
    - Date validation
    - Decision method compliance
    - Price verification with TASE
    - Problematic securities flagging
    """

    @property
    def hook_id(self) -> str:
        return "special_transactions"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def checks(self) -> List[str]:
        return [
            "chk1_duplicates",
            "chk3_dates",
            "chk4_decision",
            "chk5_sampling",
            "chk6_prices",
            "chk7_problematic"
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate required input fields."""
        if not input_data.get("manager_name"):
            return False, "manager_name is required"
        if not input_data.get("email"):
            return False, "email is required"
        return True, None

    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from Apify actors."""
        apify = ApifyClient()

        # Fetch mutual funds list
        funds_list = await apify.run_actor(
            actor_id=self.config.parameters.get("funds_list_actor"),
            input_data={}
        )

        # Fetch special transactions report
        manager_id = input_data.get("manager_id")
        transactions = await apify.run_actor(
            actor_id=self.config.parameters.get("reports_actor"),
            input_data={"manager_id": manager_id, "event_id": 5618}
        )

        return {
            "funds_list": funds_list,
            "transactions": transactions,
            "manager_name": input_data.get("manager_name"),
            "report_month": input_data.get("report_month")
        }

    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """Execute all validation checks."""
        results = []

        # CHK_1: Duplicates
        results.append(await check_duplicates(
            data["transactions"],
            data["funds_list"]
        ))

        # CHK_3: Date validation
        results.append(await check_dates(
            data["transactions"],
            data["report_month"]
        ))

        # CHK_4: Decision method
        results.append(await check_decision_method(
            data["transactions"],
            self.config.parameters
        ))

        # CHK_5: Sampling
        results.append(await check_sampling(
            data["transactions"],
            sample_size=self.config.parameters.get("sample_size", 5)
        ))

        # CHK_6: Price checks
        if not self.config.parameters.get("skip_tase_prices", True):
            results.append(await check_prices(
                data["transactions"],
                threshold=self.config.parameters.get("price_variance_threshold", 5.0)
            ))

        # CHK_7: Problematic securities
        results.append(await check_problematic_securities(
            data["transactions"]
        ))

        return results

    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult]
    ) -> Path:
        """Generate multi-sheet Excel report."""
        generator = ExcelGenerator()

        output_dir = Path("output") / input_data.get("manager_name", "unknown")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"special_transactions_report.xlsx"

        await generator.create_report(
            output_path=output_file,
            sheets=[
                ("סיכום", self._build_summary_sheet(results)),
                ("סטטוס בדיקות", self._build_status_sheet(results)),
                *[(r.check_name_he, r.findings) for r in results if r.findings]
            ]
        )

        return output_file
```

---

## 7. Configuration Format

### hooks.yaml

```yaml
# config/hooks.yaml
# Hook definitions and schedules

version: "1.0"

defaults:
  timezone: "Asia/Jerusalem"
  email:
    from: "notifications@82labs.io"
    provider: "resend"

hooks:
  # ============================================
  # Hook #1: Monthly Report Validation
  # ============================================
  monthly_report:
    id: "monthly_report"
    name: "Monthly Report Validation"
    name_he: "בקרה אוטומטית על דוח חודשי"
    description: "Validates monthly fund holdings reports against Magna list"
    status: "active"

    schedule:
      enabled: true
      cron: "0 9 5 * *"         # 5th of every month at 09:00
      timezone: "Asia/Jerusalem"

    parameters:
      # Price check threshold (percentage)
      price_variance_threshold: 7.5

      # Asset types flagged as unusual
      unusual_asset_types:
        - 16
        - 21
        - 22
        - 23
        - 24
        - 52
        - 53
        - 57
        - 58
        - 99
        - 101
        - 112
        - 201
        - 207
        - 209

      # Required asset type combinations (Clause 214)
      # Key: required type, Value: triggering types
      required_combinations:
        111: [38, 42, 45, 47, 49, 56]  # If any >= 100,000 ILS
        212: [326, 327]
        213: [319]
        208: [307]
        210: [310]

      # Minimum value to trigger combination check
      combination_threshold_ils: 100000

      # Apify actor IDs
      funds_list_actor: "K9WppTziYC3n2vxTu"
      reports_actor: "5lhI6O39Qbgv9O0gs"

    checks:
      - id: "completeness"
        name: "Completeness Check"
        name_he: "בדיקת שלמות"
        description: "Cross-reference Magna vs Manager reports"
        enabled: true

      - id: "unusual_assets"
        name: "Unusual Asset Types"
        name_he: "סוגי נכסים חריגים"
        description: "Flag unusual asset types with value > 0"
        enabled: true

      - id: "new_assets"
        name: "New Assets"
        name_he: "נכסים חדשים"
        description: "New assets added since previous month"
        enabled: true

      - id: "quantity_changes"
        name: "Quantity Changes"
        name_he: "שינויים בכמות"
        description: "Unusual quantity changes month-over-month"
        enabled: true

      - id: "clause_328"
        name: "Clause 328"
        name_he: "סעיף 328"
        description: "Borrowed quantity consistency check"
        enabled: true

      - id: "required_combinations"
        name: "Required Combinations"
        name_he: "שילובים נדרשים"
        description: "Required asset type combinations (Clause 214)"
        enabled: true

      - id: "price_reasonableness"
        name: "Price Reasonableness"
        name_he: "סבירות מחירים"
        description: "Price ratio validation"
        enabled: true

    email:
      enabled: true
      template: "monthly_report"
      recipients_from_input: true
      cc:
        - "elay.g@82labs.io"

    output:
      format: "xlsx"
      include_review_columns: true  # האם תקין?, שם הבודק

  # ============================================
  # Hook #2: Special Transactions Validation
  # ============================================
  special_transactions:
    id: "special_transactions"
    name: "Special Transactions Validation"
    name_he: "בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה"
    description: "Validates coordinated/off-exchange trades"
    status: "development"

    schedule:
      enabled: false              # Manual trigger only for now
      cron: "0 10 5 * *"          # Planned: 5th at 10:00
      timezone: "Asia/Jerusalem"

    parameters:
      # Price variance threshold (percentage)
      price_variance_threshold: 5.0

      # Number of random samples for manual verification
      sample_size: 5

      # Skip TASE price scraping (slow, requires Selenium)
      skip_tase_prices: true

      # Transaction types requiring decision method 1
      decision_types_requiring_1:
        - 12
        - 22

      # Transaction types requiring decision method 1 or 2
      decision_types_requiring_1_or_2:
        - 31
        - 32
        - 33
        - 34
        - 35
        - 36

      # Apify configuration
      funds_list_actor: "K9WppTziYC3n2vxTu"
      reports_actor: "5lhI6O39Qbgv9O0gs"
      event_id: 5618

    checks:
      - id: "chk1_duplicates"
        name: "Duplicates"
        name_he: "עסקאות כפולות"
        description: "Inter-fund transactions (buy/sell pairs)"
        enabled: true

      - id: "chk3_dates"
        name: "Date Validation"
        name_he: "חריגות תאריך"
        description: "Transaction dates within report month"
        enabled: true

      - id: "chk4_decision"
        name: "Decision Method"
        name_he: "שיטת ההחלטה"
        description: "Decision method and דחצ voting rules"
        enabled: true
        sub_checks:
          - id: "chk4a_method_required"
            name_he: "שיטת החלטה נדרשת"
          - id: "chk4g_dachatz_vote_required"
            name_he: "הצבעת דח״צ נדרשת"
          - id: "chk4d_dachatz_vote_2_flag"
            name_he: "דח״צ הצביע 2"

      - id: "chk5_sampling"
        name: "Sampling"
        name_he: "דגימות"
        description: "Random samples for manual verification"
        enabled: true

      - id: "chk6_prices"
        name: "TASE Prices"
        name_he: "בדיקות מחיר"
        description: "Cross-check with TASE market data"
        enabled: true
        sub_checks:
          - id: "chk6a_tase_variance"
            name_he: "סטיית מחיר מהבורסה"
          - id: "chk6g_internal_discrepancy"
            name_he: "פער מחיר פנימי"

      - id: "chk7_problematic"
        name: "Problematic Securities"
        name_he: "ניירות בעייתיים"
        description: "Securities on warning/halt/restricted lists"
        enabled: true

    email:
      enabled: true
      template: "special_transactions"
      recipients_from_input: true
      include_samples: true       # Include transaction samples in email body
      cc:
        - "elay.g@82labs.io"

    output:
      format: "xlsx"
      sheets:
        - "סיכום"
        - "סטטוס בדיקות"
        - "עסקאות כפולות"
        - "חריגות תאריך"
        - "חריגות החלטה"
        - "דגימות"
        - "בדיקות מחיר"
        - "ניירות בעייתיים"
        - "מחוץ לטווח"

  # ============================================
  # Hook #3: Financial Report Validation (Future)
  # ============================================
  financial_report:
    id: "financial_report"
    name: "Financial Report Validation"
    name_he: "בדיקת דוח כספי אוטומטית"
    description: "Automated financial report validation"
    status: "specification"
    planned_release: "Q1 2026"

    schedule:
      enabled: false

    parameters: {}
    checks: []

    email:
      enabled: false
```

### managers.yaml

```yaml
# config/managers.yaml
# Fund manager configuration

version: "1.0"

managers:
  migdal:
    id: "10040"
    name_he: "מגדל"
    name_en: "Migdal"
    enabled: true
    contact_email: ""

  ayalon:
    id: "10054"
    name_he: "איילון"
    name_en: "Ayalon"
    enabled: true
    contact_email: ""

  kesem:
    id: "10047"
    name_he: "קסם"
    name_en: "Kesem"
    enabled: true
    contact_email: ""

  sigma:
    id: "10048"
    name_he: "סיגמא"
    name_en: "Sigma"
    enabled: true
    contact_email: ""

  forest:
    id: "10082"
    name_he: "פורסט"
    name_en: "Forest"
    enabled: true
    contact_email: ""

  harel:
    id: "10031"
    name_he: "הראל"
    name_en: "Harel"
    enabled: true
    contact_email: ""

  analyst:
    id: "10019"
    name_he: "אנליסט"
    name_en: "Analyst"
    enabled: true
    contact_email: ""

  meitav:
    id: "10083"
    name_he: "מיטב"
    name_en: "Meitav"
    enabled: true
    contact_email: ""

  ibi:
    id: "10068"
    name_he: "איביאי"
    name_en: "IBI"
    enabled: true
    contact_email: ""

  altshuler:
    id: "10017"
    name_he: "אלטשולר-שחם"
    name_en: "Altshuler Shaham"
    enabled: true
    contact_email: ""

# Lookup helpers (generated at load time)
# by_id: {"10040": "migdal", ...}
# by_name_he: {"מגדל": "migdal", ...}
```

### environments/production.yaml

```yaml
# config/environments/production.yaml
# Production environment configuration

environment: "production"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false

database:
  url: "${DATABASE_URL}"
  pool_size: 10
  max_overflow: 20

redis:
  url: "${REDIS_URL}"
  enabled: true

email:
  provider: "resend"
  api_key: "${RESEND_API_KEY}"
  from_address: "notifications@82labs.io"
  from_name: "Mizrahi Compliance"

apify:
  token: "${APIFY_API_TOKEN}"
  timeout_seconds: 300
  max_retries: 3

logging:
  level: "INFO"
  format: "json"

monitoring:
  sentry_dsn: "${SENTRY_DSN}"
  enabled: true

cors:
  allowed_origins:
    - "https://mizrahi-compliance.82labs.io"
    - "https://mizrahi-smart-tools-portal.vercel.app"
```

### environments/development.yaml

```yaml
# config/environments/development.yaml
# Development environment configuration

environment: "development"

server:
  host: "127.0.0.1"
  port: 8000
  workers: 1
  reload: true

database:
  url: "sqlite:///./dev.db"
  echo: true

redis:
  enabled: false

email:
  provider: "console"  # Print to console instead of sending

apify:
  token: "${APIFY_API_TOKEN}"
  timeout_seconds: 60
  mock_enabled: true   # Use cached test data when available

logging:
  level: "DEBUG"
  format: "text"

monitoring:
  enabled: false

cors:
  allowed_origins:
    - "http://localhost:5173"
    - "http://localhost:3000"
```

---

## 8. API Design

### RESTful Endpoints

```
Base URL: /api/v1

# ==========================================
# Hooks
# ==========================================

GET    /hooks
       List all hooks with status and schedule info
       Response: { hooks: [...] }

GET    /hooks/{hook_id}
       Get hook details including config and recent runs
       Response: { hook: {...}, recent_jobs: [...] }

POST   /hooks/{hook_id}/run
       Trigger manual hook execution
       Body: { manager_name: "מגדל", email: "user@example.com", ... }
       Response: { job_id: "uuid", status: "queued" }

PATCH  /hooks/{hook_id}/config
       Update hook parameters (admin only)
       Body: { parameters: {...} }
       Response: { hook: {...} }

# ==========================================
# Jobs
# ==========================================

GET    /jobs
       List jobs with pagination and filters
       Query: ?hook_id=X&status=X&page=1&limit=20
       Response: { jobs: [...], total: N, page: 1 }

GET    /jobs/{job_id}
       Get job status and results
       Response: { job: {...}, checks: [...] }

GET    /jobs/{job_id}/stream
       SSE endpoint for real-time progress updates
       Response: Server-Sent Events

GET    /jobs/{job_id}/download
       Download job output file (Excel report)
       Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

DELETE /jobs/{job_id}
       Cancel a running job
       Response: { success: true }

# ==========================================
# Schedules
# ==========================================

GET    /schedules
       List all hook schedules
       Response: { schedules: [...] }

PATCH  /schedules/{hook_id}
       Update hook schedule
       Body: { enabled: true, cron: "0 9 5 * *" }
       Response: { schedule: {...} }

# ==========================================
# Managers
# ==========================================

GET    /managers
       List all fund managers
       Response: { managers: [...] }

GET    /managers/{manager_id}
       Get manager details and recent jobs
       Response: { manager: {...}, recent_jobs: [...] }

# ==========================================
# Health
# ==========================================

GET    /health
       Health check with dependency status
       Response: { status: "healthy", checks: {...} }

GET    /health/ready
       Readiness probe for container orchestration
       Response: { ready: true }
```

### TypeScript API Types

```typescript
// apps/web/src/api/types.ts

// ==========================================
// Hooks
// ==========================================

export interface Hook {
  id: string;
  name: string;
  name_he: string;
  description: string;
  status: "active" | "development" | "specification";
  schedule: HookSchedule;
  checks: HookCheck[];
  parameters: Record<string, unknown>;
}

export interface HookSchedule {
  enabled: boolean;
  cron: string | null;
  timezone: string;
  next_run: string | null;  // ISO datetime
  last_run: string | null;  // ISO datetime
}

export interface HookCheck {
  id: string;
  name: string;
  name_he: string;
  description: string;
  enabled: boolean;
}

// ==========================================
// Jobs
// ==========================================

export interface Job {
  id: string;
  hook_id: string;
  manager_name: string;
  manager_id: string;
  status: JobStatus;
  trigger: "scheduled" | "manual" | "api";
  progress: JobProgress;
  result: JobResult | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export type JobStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface JobProgress {
  current_check: string | null;
  checks_completed: number;
  checks_total: number;
  percent: number;
  message: string;
}

export interface JobResult {
  status: "success" | "partial" | "failed";
  message: string;
  checks: CheckResult[];
  output_file: string | null;
  email_sent: boolean;
  email_recipients: string[];
  duration_seconds: number;
}

export interface CheckResult {
  check_id: string;
  check_name: string;
  check_name_he: string;
  status: "pass" | "fail" | "warning" | "skipped";
  message: string;
  findings_count: number;
  duration_ms: number;
}

// ==========================================
// Managers
// ==========================================

export interface Manager {
  id: string;
  key: string;
  name_he: string;
  name_en: string;
  enabled: boolean;
}

// ==========================================
// API Requests
// ==========================================

export interface RunHookRequest {
  manager_name: string;
  email: string;
  price_threshold?: number;
  skip_tase_prices?: boolean;
}

export interface UpdateScheduleRequest {
  enabled?: boolean;
  cron?: string;
}

// ==========================================
// API Responses
// ==========================================

export interface HooksResponse {
  hooks: Hook[];
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  page: number;
  limit: number;
}

export interface RunHookResponse {
  job_id: string;
  status: "queued";
  message: string;
}
```

### FastAPI Router Example

```python
# apps/api/src/routers/hooks.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

from ..services.hook_runner import HookRunner
from ..services.job_service import JobService
from ..dependencies import get_hook_config

router = APIRouter(prefix="/hooks", tags=["hooks"])

class RunHookRequest(BaseModel):
    manager_name: str
    email: EmailStr
    price_threshold: Optional[float] = None
    skip_tase_prices: Optional[bool] = True

class RunHookResponse(BaseModel):
    job_id: UUID
    status: str = "queued"
    message: str

@router.get("")
async def list_hooks():
    """List all available hooks with their status and schedules."""
    hooks = await get_all_hooks_with_status()
    return {"hooks": hooks}

@router.get("/{hook_id}")
async def get_hook(hook_id: str):
    """Get hook details including configuration and recent runs."""
    hook = await get_hook_config(hook_id)
    if not hook:
        raise HTTPException(status_code=404, detail=f"Hook '{hook_id}' not found")

    recent_jobs = await JobService.get_recent_by_hook(hook_id, limit=10)
    return {"hook": hook, "recent_jobs": recent_jobs}

@router.post("/{hook_id}/run", response_model=RunHookResponse)
async def run_hook(
    hook_id: str,
    request: RunHookRequest,
    background_tasks: BackgroundTasks
):
    """Trigger manual hook execution."""
    hook_config = await get_hook_config(hook_id)
    if not hook_config:
        raise HTTPException(status_code=404, detail=f"Hook '{hook_id}' not found")

    # Create job record
    job = await JobService.create(
        hook_id=hook_id,
        manager_name=request.manager_name,
        trigger="manual",
        input_data=request.model_dump()
    )

    # Queue background execution
    background_tasks.add_task(
        HookRunner.execute,
        job_id=job.id,
        hook_id=hook_id,
        input_data=request.model_dump()
    )

    return RunHookResponse(
        job_id=job.id,
        status="queued",
        message=f"Job queued for {request.manager_name}"
    )
```

---

## 9. Hosting Recommendations

### Comparison Matrix

| Platform | Pros | Cons | Monthly Cost | Recommended |
|----------|------|------|--------------|-------------|
| **Railway** | Monorepo-native, built-in PostgreSQL, cron jobs, easy Docker | Limited free tier | $20-50 | **Yes** |
| **Render** | Simple, good free tier, native cron | Slower builds | $25-40 | Yes |
| **Fly.io** | Edge deployment, excellent Docker | More complex setup | $15-30 | Maybe |
| **DigitalOcean App Platform** | Familiar, good pricing | Less monorepo support | $25-50 | Maybe |
| **Self-hosted (VPS)** | Full control, existing infra | Manual maintenance | $20-40 | Fallback |

### Recommended: Railway

**Why Railway is ideal for this project:**

1. **Monorepo Support**: Detects and builds multiple services from one repo
2. **Built-in PostgreSQL**: One-click database provisioning
3. **Cron Jobs**: Native support for scheduled tasks (replaces n8n schedules)
4. **Docker Support**: Full Dockerfile support for custom builds
5. **Preview Environments**: Auto-deploy PR branches for testing
6. **Secrets Management**: Secure environment variable handling
7. **Logs & Monitoring**: Built-in log aggregation

**Railway Configuration:**

```toml
# railway.toml (root)
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

**Dockerfile (Multi-stage):**

```dockerfile
# Dockerfile

# ============================================
# Stage 1: Frontend Build
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy workspace files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source
COPY apps/web ./apps/web
COPY packages/ui ./packages/ui

# Build frontend
RUN pnpm --filter web build

# ============================================
# Stage 2: Python Dependencies
# ============================================
FROM python:3.12-slim AS python-builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install uv

# Copy Python package files
COPY apps/api/pyproject.toml apps/api/uv.lock ./apps/api/
COPY packages/hooks/pyproject.toml ./packages/hooks/
COPY packages/shared/pyproject.toml ./packages/shared/

# Install dependencies
RUN cd apps/api && uv sync --frozen

# ============================================
# Stage 3: Production Image
# ============================================
FROM python:3.12-slim AS production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment
COPY --from=python-builder /app/apps/api/.venv /app/.venv

# Copy Python source
COPY apps/api/src ./apps/api/src
COPY packages/hooks/src ./packages/hooks/src
COPY packages/shared/src ./packages/shared/src
COPY config ./config

# Copy built frontend
COPY --from=frontend-builder /app/apps/web/dist ./apps/web/dist

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/api/src:/app/packages/hooks/src:/app/packages/shared/src"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 10. Additional Requirements

### 10.1 Job History & Audit Log

**Database Schema:**

```python
# apps/api/src/db/models.py

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
import json

class Job(SQLModel, table=True):
    """Job execution record for audit trail."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hook_id: str = Field(index=True)
    manager_id: Optional[str] = Field(default=None, index=True)
    manager_name: str

    # Execution info
    status: str = Field(default="queued", index=True)  # queued, running, completed, failed, cancelled
    trigger: str  # scheduled, manual, api
    triggered_by: Optional[str] = None  # email or API key identifier

    # Input/Output
    input_data: str = Field(default="{}")  # JSON
    result_summary: Optional[str] = None   # JSON
    output_path: Optional[str] = None
    error_message: Optional[str] = None

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Relationships
    logs: List["JobLog"] = Relationship(back_populates="job")

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def input_dict(self) -> dict:
        return json.loads(self.input_data)

    @property
    def result_dict(self) -> Optional[dict]:
        if self.result_summary:
            return json.loads(self.result_summary)
        return None


class JobLog(SQLModel, table=True):
    """Detailed job execution logs."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    job_id: UUID = Field(foreign_key="job.id", index=True)

    level: str  # DEBUG, INFO, WARNING, ERROR
    check_id: Optional[str] = None
    message: str
    details: Optional[str] = None  # JSON for structured data

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    job: Job = Relationship(back_populates="logs")


class ScheduleOverride(SQLModel, table=True):
    """Track manual schedule changes (for audit)."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hook_id: str = Field(index=True)

    previous_cron: Optional[str]
    new_cron: Optional[str]
    previous_enabled: bool
    new_enabled: bool

    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
```

### 10.2 Real-Time Progress Updates (SSE)

```python
# apps/api/src/routers/jobs.py

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """
    Server-Sent Events endpoint for real-time job progress.

    Events:
    - progress: { status, current_check, percent, message }
    - check_complete: { check_id, status, findings_count }
    - complete: { status, message, output_file }
    - error: { message }
    """
    async def event_generator():
        while True:
            job = await JobService.get(job_id)

            if job is None:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": "Job not found"})
                }
                break

            # Send progress update
            yield {
                "event": "progress",
                "data": json.dumps({
                    "status": job.status,
                    "current_check": job.current_check,
                    "checks_completed": job.checks_completed,
                    "checks_total": job.checks_total,
                    "percent": job.progress_percent,
                    "message": job.progress_message
                })
            }

            # Check for completion
            if job.status in ("completed", "failed", "cancelled"):
                yield {
                    "event": "complete",
                    "data": json.dumps({
                        "status": job.status,
                        "message": job.result_dict.get("message") if job.result_dict else None,
                        "output_file": job.output_path,
                        "duration_seconds": job.duration_seconds
                    })
                }
                break

            await asyncio.sleep(1)  # Poll every second

    return EventSourceResponse(event_generator())
```

**Frontend Hook:**

```typescript
// apps/web/src/hooks/useJobStream.ts

import { useState, useEffect, useCallback } from "react";

interface JobProgress {
  status: string;
  current_check: string | null;
  checks_completed: number;
  checks_total: number;
  percent: number;
  message: string;
}

export function useJobStream(jobId: string | null) {
  const [progress, setProgress] = useState<JobProgress | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(`/api/v1/jobs/${jobId}/stream`);

    eventSource.addEventListener("progress", (e) => {
      setProgress(JSON.parse(e.data));
    });

    eventSource.addEventListener("complete", (e) => {
      setProgress(JSON.parse(e.data));
      setIsComplete(true);
      eventSource.close();
    });

    eventSource.addEventListener("error", (e) => {
      setError("Connection lost");
      eventSource.close();
    });

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  return { progress, isComplete, error };
}
```

### 10.3 Notification System

```yaml
# config/notifications.yaml

version: "1.0"

channels:
  email:
    enabled: true
    provider: "resend"  # resend | smtp | console

  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"

  webhook:
    enabled: false
    url: "${CUSTOM_WEBHOOK_URL}"

templates:
  job_success:
    email:
      subject: "✅ {hook_name} - {manager_name} - Completed"
    slack:
      text: "✅ *{hook_name}* completed for *{manager_name}*"
      color: "good"

  job_partial:
    email:
      subject: "⚠️ {hook_name} - {manager_name} - Completed with warnings"
    slack:
      text: "⚠️ *{hook_name}* for *{manager_name}* completed with {warning_count} warnings"
      color: "warning"

  job_failed:
    email:
      subject: "❌ {hook_name} - {manager_name} - Failed"
    slack:
      text: "❌ *{hook_name}* failed for *{manager_name}*: {error_message}"
      color: "danger"

routing:
  # Which channels to use for each event type
  on_success:
    - email

  on_partial:
    - email
    - slack

  on_failure:
    - email
    - slack

recipients:
  default:
    - "elay.g@82labs.io"

  alerts:
    - "ops@82labs.io"
```

### 10.4 Health Checks & Monitoring

```python
# apps/api/src/routers/health.py

from fastapi import APIRouter
from datetime import datetime
import asyncio

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Comprehensive health check with dependency status.
    """
    checks = await asyncio.gather(
        check_database(),
        check_redis(),
        check_apify(),
        check_email_service(),
        return_exceptions=True
    )

    db_status, redis_status, apify_status, email_status = checks

    all_healthy = all(
        isinstance(c, dict) and c.get("healthy", False)
        for c in checks
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": db_status if isinstance(db_status, dict) else {"healthy": False, "error": str(db_status)},
            "redis": redis_status if isinstance(redis_status, dict) else {"healthy": False, "error": str(redis_status)},
            "apify": apify_status if isinstance(apify_status, dict) else {"healthy": False, "error": str(apify_status)},
            "email": email_status if isinstance(email_status, dict) else {"healthy": False, "error": str(email_status)},
        }
    }

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes/container orchestration.
    Returns 200 if the service is ready to accept traffic.
    """
    # Check critical dependencies only
    db_ok = await check_database_connection()

    if not db_ok:
        return {"ready": False}, 503

    return {"ready": True}

@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe - just confirms the process is running.
    """
    return {"alive": True}
```

### 10.5 Rate Limiting

```python
# packages/shared/src/mizrahi_shared/rate_limit.py

import asyncio
from functools import wraps
from typing import Callable, Any

# Semaphores for external service rate limiting
_SEMAPHORES = {
    "apify": asyncio.Semaphore(3),      # Max 3 concurrent Apify calls
    "tase": asyncio.Semaphore(1),        # Max 1 concurrent TASE scrape (be gentle)
    "email": asyncio.Semaphore(5),       # Max 5 concurrent email sends
}

def rate_limited(service: str):
    """
    Decorator to rate limit calls to external services.

    Usage:
        @rate_limited("apify")
        async def call_apify_actor(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            semaphore = _SEMAPHORES.get(service)
            if semaphore is None:
                return await func(*args, **kwargs)

            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper
    return decorator
```

---

## 11. Migration Plan

### Phase 1: Repository Setup (Week 1)

**Tasks:**
- [ ] Create new GitHub repository `mizrahi-compliance-platform`
- [ ] Initialize monorepo structure with pnpm workspaces
- [ ] Set up base configuration files (package.json, pnpm-workspace.yaml)
- [ ] Create `.github/workflows/ci.yml` for basic linting
- [ ] Move frontend code to `apps/web/`
- [ ] Verify frontend builds successfully

**Deliverables:**
- Working monorepo with frontend only
- CI pipeline running on PRs

### Phase 2: Shared Package Extraction (Week 1-2)

**Tasks:**
- [ ] Create `packages/shared/` Python package
- [ ] Extract `FUND_MANAGERS` and constants to `config.py`
- [ ] Extract data models to `models.py`
- [ ] Extract Apify client to `apify.py`
- [ ] Extract email service to `email.py`
- [ ] Extract Excel utilities to `excel.py`
- [ ] Add unit tests for shared utilities

**Deliverables:**
- `packages/shared/` with all common utilities
- No more duplicated constants

### Phase 3: Hook Refactoring (Week 2-3)

**Tasks:**
- [ ] Create `packages/hooks/` Python package
- [ ] Implement `BaseHook` abstract class
- [ ] Implement hook registry
- [ ] Refactor `fund_automation_complete.py` → `monthly_report/`
- [ ] Refactor `mizrahi_special_transactions.py` → `special_transactions/`
- [ ] Add integration tests for hooks

**Deliverables:**
- Both hooks working with new architecture
- All checks modularized into separate files

### Phase 4: API Development (Week 3-4)

**Tasks:**
- [ ] Create `apps/api/` FastAPI application
- [ ] Implement database models with SQLModel
- [ ] Set up Alembic migrations
- [ ] Implement `/hooks` endpoints
- [ ] Implement `/jobs` endpoints with SSE
- [ ] Implement `/schedules` endpoints
- [ ] Add APScheduler for cron jobs
- [ ] Add background worker for job processing

**Deliverables:**
- Working API with all endpoints
- Job queue with real-time updates
- Scheduled hook execution

### Phase 5: Frontend Integration (Week 4-5)

**Tasks:**
- [ ] Update frontend to use new API client
- [ ] Create Dashboard page with hook overview
- [ ] Create HookRunner page with form submission
- [ ] Create JobHistory page with job listing
- [ ] Add real-time progress with SSE
- [ ] Add schedule management UI
- [ ] Update styling and UX

**Deliverables:**
- Fully integrated frontend
- Real-time job progress
- Self-service schedule management

### Phase 6: Deployment & Migration (Week 5-6)

**Tasks:**
- [ ] Create Dockerfile (multi-stage)
- [ ] Set up Railway project
- [ ] Configure PostgreSQL database
- [ ] Set up environment variables
- [ ] Deploy to staging
- [ ] Run parallel testing (old system vs new)
- [ ] Migrate DNS/routing
- [ ] Sunset n8n workflows
- [ ] Update documentation

**Deliverables:**
- Production deployment on Railway
- Old systems decommissioned
- Full documentation

### Timeline Summary

```
Week 1:  [████████████████████] Repository Setup + Shared Package Start
Week 2:  [████████████████████] Shared Package + Hook Refactoring Start
Week 3:  [████████████████████] Hook Refactoring + API Development Start
Week 4:  [████████████████████] API Development + Frontend Integration Start
Week 5:  [████████████████████] Frontend Integration + Deployment Start
Week 6:  [████████████████████] Deployment + Migration Complete
```

---

## 12. Technical Decisions

### Why These Choices?

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Monorepo Tool** | pnpm workspaces | Fast, efficient disk usage, good monorepo support |
| **Frontend Framework** | React + Vite (keep existing) | Already built, works well, team familiarity |
| **Backend Framework** | FastAPI | Modern async Python, auto-docs, type safety |
| **Database** | PostgreSQL + SQLModel | Robust, good for audit logs, SQLModel = type safety |
| **Job Queue** | In-memory + database | Simple, sufficient for workload, no Redis needed initially |
| **Scheduler** | APScheduler | Pure Python, no external deps, cron syntax |
| **Email** | Resend (keep existing) | Already configured, good deliverability |
| **Hosting** | Railway | Best monorepo DX, built-in Postgres, cron support |
| **Config Format** | YAML | Human-readable, supports complex structures |
| **Python Package Manager** | uv | Fast, modern, lockfile support |

### Alternatives Considered

| Decision | Alternative | Why Not |
|----------|-------------|---------|
| Monorepo Tool | Nx, Turborepo | Overkill for 2 apps, pnpm sufficient |
| Job Queue | Celery + Redis | Added complexity, not needed for workload |
| Database | SQLite | Not suitable for production concurrent access |
| Scheduler | Celery Beat | Requires Redis/RabbitMQ infrastructure |
| Hosting | Kubernetes | Over-engineered for this scale |

---

## Appendix A: Development Workflow

### Local Development

```bash
# Clone repository
git clone https://github.com/82labs/mizrahi-compliance-platform.git
cd mizrahi-compliance-platform

# Install dependencies
pnpm install
cd apps/api && uv sync && cd ../..

# Copy environment variables
cp .env.example .env
# Edit .env with your credentials

# Start development servers
./scripts/dev.sh
# Or manually:
# Terminal 1: cd apps/web && pnpm dev
# Terminal 2: cd apps/api && uv run uvicorn main:app --reload

# Run tests
./scripts/test.sh

# Run linting
pnpm lint
cd apps/api && uv run ruff check .
```

### Git Workflow

```
main          ─────●─────●─────●─────●─────►
                   │     │     │     │
feature/xxx   ─────●─────●─────┘     │
                         │           │
feature/yyy   ───────────●───────────┘
```

1. Create feature branch from `main`
2. Make changes, commit with conventional commits
3. Open PR, CI runs automatically
4. Review, approve, squash merge
5. Auto-deploy to staging on merge
6. Manual promotion to production

### Conventional Commits

```
feat(hooks): add financial report hook skeleton
fix(api): handle missing manager_id in job creation
docs(readme): update development setup instructions
refactor(shared): extract email templates to config
test(hooks): add unit tests for price reasonableness check
chore(deps): update fastapi to 0.110.0
```

---

## Appendix B: Security Considerations

### Secrets Management

| Secret | Storage | Access |
|--------|---------|--------|
| `APIFY_API_TOKEN` | Railway env vars | API only |
| `RESEND_API_KEY` | Railway env vars | API only |
| `DATABASE_URL` | Railway auto-injected | API only |
| `SLACK_WEBHOOK_URL` | Railway env vars | API only |

### Access Control (Future)

- [ ] API key authentication for external integrations
- [ ] Role-based access for admin vs user
- [ ] Audit logging for all schedule changes

### Data Handling

- No PII stored beyond email addresses
- Job outputs auto-deleted after 30 days
- Database backups encrypted at rest

---

## Appendix C: Monitoring & Alerting

### Metrics to Track

| Metric | Alert Threshold |
|--------|-----------------|
| Job failure rate | > 10% in 1 hour |
| Job duration | > 10 minutes |
| API response time | > 2 seconds (p95) |
| Database connections | > 80% pool |

### Log Aggregation

All logs shipped to Railway's built-in logging with:
- Structured JSON format in production
- Request ID correlation
- Job ID tagging

---

**Document End**

*This architecture plan will be updated as implementation progresses.*
