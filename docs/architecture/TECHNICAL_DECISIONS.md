# Technical Decisions

This document covers technology choices, alternatives considered, and appendices
with development workflow, security considerations, and monitoring.

**Related Documents:**

- [System Design](./SYSTEM_DESIGN.md) - Architecture overview
- [Deployment](./DEPLOYMENT.md) - Hosting setup

---

## Table of Contents

1. [Technology Choices](#technology-choices)
2. [Alternatives Considered](#alternatives-considered)
3. [Appendix A: Development Workflow](#appendix-a-development-workflow)
4. [Appendix B: Security Considerations](#appendix-b-security-considerations)
5. [Appendix C: Monitoring & Alerting](#appendix-c-monitoring--alerting)

---

## Technology Choices

| Decision                   | Choice                       | Rationale                                                  |
| -------------------------- | ---------------------------- | ---------------------------------------------------------- |
| **Monorepo Tool**          | pnpm workspaces              | Fast, efficient disk usage, good monorepo support          |
| **Frontend Framework**     | React + Vite (keep existing) | Already built, works well, team familiarity                |
| **Backend Framework**      | FastAPI                      | Modern async Python, auto-docs, type safety                |
| **Database**               | PostgreSQL + SQLModel        | Robust, good for audit logs, SQLModel = type safety        |
| **Job Queue**              | In-memory + database         | Simple, sufficient for workload, no Redis needed initially |
| **Scheduler**              | APScheduler                  | Pure Python, no external deps, cron syntax                 |
| **Email**                  | Resend (keep existing)       | Already configured, good deliverability                    |
| **Hosting**                | Railway                      | Best monorepo DX, built-in Postgres, cron support          |
| **Config Format**          | YAML                         | Human-readable, supports complex structures                |
| **Python Package Manager** | uv                           | Fast, modern, lockfile support                             |

---

## Alternatives Considered

| Decision      | Alternative    | Why Not                                       |
| ------------- | -------------- | --------------------------------------------- |
| Monorepo Tool | Nx, Turborepo  | Overkill for 2 apps, pnpm sufficient          |
| Job Queue     | Celery + Redis | Added complexity, not needed for workload     |
| Database      | SQLite         | Not suitable for production concurrent access |
| Scheduler     | Celery Beat    | Requires Redis/RabbitMQ infrastructure        |
| Hosting       | Kubernetes     | Over-engineered for this scale                |

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

| Secret              | Storage               | Access   |
| ------------------- | --------------------- | -------- |
| `APIFY_API_TOKEN`   | Railway env vars      | API only |
| `RESEND_API_KEY`    | Railway env vars      | API only |
| `DATABASE_URL`      | Railway auto-injected | API only |
| `SLACK_WEBHOOK_URL` | Railway env vars      | API only |

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

| Metric               | Alert Threshold   |
| -------------------- | ----------------- |
| Job failure rate     | > 10% in 1 hour   |
| Job duration         | > 10 minutes      |
| API response time    | > 2 seconds (p95) |
| Database connections | > 80% pool        |

### Log Aggregation

All logs shipped to Railway's built-in logging with:

- Structured JSON format in production
- Request ID correlation
- Job ID tagging

---

**Document End**

_This architecture plan will be updated as implementation progresses._
