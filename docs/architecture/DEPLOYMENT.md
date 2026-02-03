# Deployment

This document covers hosting recommendations, platform comparison, and Docker
configuration.

**Related Documents:**

- [System Design](./SYSTEM_DESIGN.md) - Overall architecture
- [Migration Plan](./MIGRATION_PLAN.md) - Deployment phases

---

## Table of Contents

1. [Hosting Comparison](#hosting-comparison)
2. [Recommended: Railway](#recommended-railway)
3. [Docker Configuration](#docker-configuration)

---

## Hosting Comparison

| Platform                      | Pros                                                         | Cons                  | Monthly Cost | Recommended |
| ----------------------------- | ------------------------------------------------------------ | --------------------- | ------------ | ----------- |
| **Railway**                   | Monorepo-native, built-in PostgreSQL, cron jobs, easy Docker | Limited free tier     | $20-50       | **Yes**     |
| **Render**                    | Simple, good free tier, native cron                          | Slower builds         | $25-40       | Yes         |
| **Fly.io**                    | Edge deployment, excellent Docker                            | More complex setup    | $15-30       | Maybe       |
| **DigitalOcean App Platform** | Familiar, good pricing                                       | Less monorepo support | $25-50       | Maybe       |
| **Self-hosted (VPS)**         | Full control, existing infra                                 | Manual maintenance    | $20-40       | Fallback    |

---

## Recommended: Railway

**Why Railway is ideal for this project:**

1. **Monorepo Support**: Detects and builds multiple services from one repo
2. **Built-in PostgreSQL**: One-click database provisioning
3. **Cron Jobs**: Native support for scheduled tasks (replaces n8n schedules)
4. **Docker Support**: Full Dockerfile support for custom builds
5. **Preview Environments**: Auto-deploy PR branches for testing
6. **Secrets Management**: Secure environment variable handling
7. **Logs & Monitoring**: Built-in log aggregation

### Railway Configuration

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

---

## Docker Configuration

### Multi-stage Dockerfile

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

**Next:** [Additional Requirements](./ADDITIONAL_REQUIREMENTS.md)
