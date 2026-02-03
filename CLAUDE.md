# Project: Mizrahi Compliance Platform

Regulatory compliance validation platform for Israeli mutual funds managed by
Mizrahi Tefachot trustee. Automates validation of monthly reports and special
transactions against regulatory requirements.

## Tech Stack

### Frontend (apps/web/)

- React 18.3 + TypeScript 5.8
- Vite 5.4 (build tool)
- TailwindCSS 3.4 + shadcn/ui (Radix primitives)
- React Query (data fetching)
- React Hook Form + Zod (forms/validation)
- Recharts (visualizations)

### Backend (apps/api/)

- Python 3.11+
- FastAPI 0.109+
- SQLModel + Alembic (database)
- Pydantic v2 (validation)
- APScheduler (task scheduling)
- uv (package manager)

### Packages

- `packages/hooks/` - Validation hook implementations
- `packages/shared/` - Shared utilities, models, config

### External Services

- Apify - Web scraping (TASE Maya)
- Resend - Email notifications
- PostgreSQL (production) / SQLite (development)

## Project Structure

```
mizrahi-compliance-platform/
├── apps/
│   ├── web/                 # React frontend
│   │   └── src/
│   │       ├── pages/       # Route pages
│   │       ├── components/  # UI components
│   │       └── hooks/       # React hooks
│   └── api/                 # FastAPI backend
│       └── src/
│           ├── routers/     # API endpoints
│           ├── services/    # Business logic
│           └── db/          # Database models
├── packages/
│   ├── hooks/               # Validation hooks
│   │   └── src/mizrahi_hooks/
│   │       ├── monthly_report/
│   │       └── special_transactions/
│   └── shared/              # Shared utilities
│       └── src/mizrahi_shared/
├── config/
│   ├── hooks.yaml           # Hook definitions
│   ├── managers.yaml        # Fund manager configs
│   └── environments/        # Environment configs
├── legacy/                  # Original scripts (reference only)
└── docs/                    # Documentation
```

## Commands

### Development

- `pnpm dev` — Run all services (frontend + API)
- `pnpm dev:web` — Frontend only (http://localhost:5173)
- `pnpm dev:api` — API only (http://localhost:8000)

### Building

- `pnpm build` — Build all packages
- `pnpm build:web` — Build frontend only

### Testing

- `pnpm test` — Run all tests
- `pnpm test:py` — Run Python tests only
- `cd apps/api && uv run pytest tests/path/to/test.py` — Run specific test

### Linting & Type Checking

- `pnpm lint` — Lint all packages
- `pnpm lint:py` — Python linting (ruff)
- `pnpm typecheck` — TypeScript type checking

### Python Package Management

- `cd apps/api && uv sync` — Install Python dependencies
- `cd apps/api && uv add <package>` — Add new dependency
- `cd apps/api && uv run <command>` — Run in virtual environment

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
- Colocate tests: `Component.tsx` → `Component.test.tsx`

### Python (Backend)

- Async functions for I/O operations
- Type hints required on all function signatures
- Pydantic models for all API request/response schemas
- Use `ruff format` for formatting, `ruff check` for linting

### Hebrew Content

- Hebrew names allowed in user-facing output (UI, reports, emails)
- Internal code uses English identifiers
- Database stores Hebrew with proper UTF-8 encoding
- Config files use Hebrew for display names (`name_he`)

## Architecture Rules

### Hook System (Template Method Pattern)

```
BaseHook.execute() orchestrates:
1. validate_input() → Validate request
2. fetch_data() → Call Apify/APIs
3. run_checks() → Execute validation checks
4. generate_report() → Create Excel output
5. send_email() → Notify recipients
```

### API Response Format

```json
{
  "data": {},
  "error": null,
  "meta": { "timestamp": "...", "version": "..." }
}
```

### Data Flow

```
Frontend → API Router → Service → Hook → Check Functions
                                       ↓
                              External APIs (Apify)
                                       ↓
                              Report Generation
                                       ↓
                              Email Notification
```

## Git Workflow

### Branch Strategy

- `main` — Production (protected, receives merges from dev only)
- `dev` — Integration (protected, receives merges from feature branches)
- `feature/<description>` — New functionality
- `fix/<description>` — Bug fixes
- `hotfix/<description>` — Urgent production fixes (from main)
- `refactor/<description>` — Code improvements
- `docs/<description>` — Documentation only
- `chore/<description>` — Build, deps, config

### Rules

- NEVER commit directly to `main` or `dev`
- Create feature branches from `dev`
- Use conventional commits: `type(scope): description`
- Squash commits before merge

### Branch Naming

- Lowercase with hyphens: `feature/user-dashboard`
- Max 50 characters for description
- Optional ticket ID: `feature/TICKET-123-description`

## Testing Rules

### When to Run Full Suite

- Major features affecting multiple modules
- Major fixes that might affect other parts
- Before merging to `dev`
- Config file changes

### When to Run Targeted Tests

- Minor features (single module)
- Minor bug fixes
- Documentation changes → No tests required

### Coverage Requirements

- New code must have tests
- All TypeScript errors must be fixed before commit
- All linting warnings must be addressed

## Security

### Critical (Compliance Platform)

- Never log fund data, transaction details, or PII
- Never expose validation rules in error messages
- All input validation happens server-side
- Audit trail for all hook executions

### General

- Never hardcode secrets — use environment variables
- Never commit .env, credentials, or API keys
- Parameterized queries only — no string concatenation
- Validate all user input

## Domain Context

### Fund Managers (10 configured)

מגדל, איילון, קסם, סיגמא, פורסט, הראל, אנליסט, מיטב, איביאי, אלטשולר-שחם

### Validation Hooks

1. **monthly_report** (Active) — Monthly fund holdings validation
2. **special_transactions** (Development) — Special transactions validation
3. **financial_report** (Planned) — Financial report validation

### Configuration Files

- `config/hooks.yaml` — Hook definitions, checks, schedules
- `config/managers.yaml` — Fund manager mappings
- `config/environments/` — Environment-specific settings

## Legacy Reference

Original implementations preserved in `legacy/` directory:

- `legacy/scripts/` — Original Python scripts
- `legacy/workflows/` — n8n workflow definitions
- `legacy/docs/` — Original documentation

Use for debugging and verifying new implementation matches original behavior.
See @docs/reference/LEGACY_FILES_REFERENCE.md for details.

## Documentation

See @docs/README.md for documentation index.

Key documents:

- @docs/architecture/ — System architecture (split into focused documents)
- @docs/guides/DEVELOPMENT.md — Development setup
- @docs/guides/HOOKS_DEVELOPMENT.md — Creating hooks
- @docs/api/API_REFERENCE.md — API endpoints
