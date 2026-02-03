# Migration Plan

This document outlines the phased migration from the current scattered
architecture to the unified monorepo.

**Related Documents:**

- [Overview](./OVERVIEW.md) - Goals and requirements
- [System Design](./SYSTEM_DESIGN.md) - Target architecture
- [Deployment](./DEPLOYMENT.md) - Hosting setup

---

## Table of Contents

1. [Phase 1: Repository Setup](#phase-1-repository-setup-week-1)
2. [Phase 2: Shared Package Extraction](#phase-2-shared-package-extraction-week-1-2)
3. [Phase 3: Hook Refactoring](#phase-3-hook-refactoring-week-2-3)
4. [Phase 4: API Development](#phase-4-api-development-week-3-4)
5. [Phase 5: Frontend Integration](#phase-5-frontend-integration-week-4-5)
6. [Phase 6: Deployment & Migration](#phase-6-deployment--migration-week-5-6)
7. [Timeline Summary](#timeline-summary)

---

## Phase 1: Repository Setup (Week 1)

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

---

## Phase 2: Shared Package Extraction (Week 1-2)

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

---

## Phase 3: Hook Refactoring (Week 2-3)

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

---

## Phase 4: API Development (Week 3-4)

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

---

## Phase 5: Frontend Integration (Week 4-5)

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

---

## Phase 6: Deployment & Migration (Week 5-6)

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

---

## Timeline Summary

```
Week 1:  [████████████████████] Repository Setup + Shared Package Start
Week 2:  [████████████████████] Shared Package + Hook Refactoring Start
Week 3:  [████████████████████] Hook Refactoring + API Development Start
Week 4:  [████████████████████] API Development + Frontend Integration Start
Week 5:  [████████████████████] Frontend Integration + Deployment Start
Week 6:  [████████████████████] Deployment + Migration Complete
```

---

**Next:** [Technical Decisions](./TECHNICAL_DECISIONS.md)
