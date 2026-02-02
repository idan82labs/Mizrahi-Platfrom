# Mizrahi Compliance Platform Documentation

Welcome to the documentation for the Mizrahi Compliance Platform.

---

## Documentation Register

Quick lookup: **Which docs cover which code areas?**

### By Code Area

| Code Area | Files Changed | Update These Docs |
|-----------|---------------|-------------------|
| **API Endpoints** | `apps/api/src/routers/*` | [API Reference](./api/API_REFERENCE.md) |
| **API Main/Config** | `apps/api/src/main.py` | [API Reference](./api/API_REFERENCE.md), [Development](./guides/DEVELOPMENT.md) |
| **Hook Implementation** | `packages/hooks/src/mizrahi_hooks/*/hook.py` | [System Documentation](./SYSTEM_DOCUMENTATION.md), [Hooks Development](./guides/HOOKS_DEVELOPMENT.md) |
| **Check Functions** | `packages/hooks/src/mizrahi_hooks/*/checks/*` | [System Documentation](./SYSTEM_DOCUMENTATION.md) |
| **Shared Models** | `packages/shared/src/mizrahi_shared/models.py` | [Hooks Development](./guides/HOOKS_DEVELOPMENT.md) |
| **Shared Utilities** | `packages/shared/src/mizrahi_shared/*` | [Hooks Development](./guides/HOOKS_DEVELOPMENT.md) |
| **Hook Config** | `config/hooks.yaml` | [System Documentation](./SYSTEM_DOCUMENTATION.md), [Development](./guides/DEVELOPMENT.md) |
| **Manager Config** | `config/managers.yaml` | [System Documentation](./SYSTEM_DOCUMENTATION.md) |
| **Frontend Pages** | `apps/web/src/pages/*` | [System Documentation](./SYSTEM_DOCUMENTATION.md) |
| **Frontend Components** | `apps/web/src/components/*` | No doc update needed (unless major) |
| **Package.json** | `package.json`, `apps/*/package.json` | [Development](./guides/DEVELOPMENT.md) |
| **Python Dependencies** | `pyproject.toml`, `apps/api/pyproject.toml` | [Development](./guides/DEVELOPMENT.md) |
| **Legacy Scripts** | `legacy/*` | [Legacy Files Reference](./reference/LEGACY_FILES_REFERENCE.md) |

### By Task

| Task | Relevant Documentation |
|------|------------------------|
| **Setting up development** | [Development Guide](./guides/DEVELOPMENT.md) |
| **Creating a new hook** | [Hooks Development](./guides/HOOKS_DEVELOPMENT.md) |
| **Adding a new check** | [Hooks Development](./guides/HOOKS_DEVELOPMENT.md), [System Documentation](./SYSTEM_DOCUMENTATION.md) |
| **Adding API endpoint** | [API Reference](./api/API_REFERENCE.md) |
| **Batch processing** | [Batch Processing](./guides/BATCH_PROCESSING.md) |
| **Debugging hooks** | [Legacy Files Reference](./reference/LEGACY_FILES_REFERENCE.md), [System Guide](./guides/SYSTEM_GUIDE.md) |
| **Understanding architecture** | [Architecture](./ARCHITECTURE.md) |
| **Quick commands** | [Cheatsheet](./CHEATSHEET.md) |

---

## Documentation Index

### Overview

| Document | Description |
|----------|-------------|
| [System Documentation](./SYSTEM_DOCUMENTATION.md) | Complete system overview, architecture, and component details |
| [Architecture Plan](./ARCHITECTURE.md) | Monorepo architecture design and implementation plan |
| [Cheatsheet](./CHEATSHEET.md) | Quick reference commands and common operations |

### Guides

| Document | Description |
|----------|-------------|
| [Development Guide](./guides/DEVELOPMENT.md) | Setting up development environment, coding standards |
| [Hooks Development](./guides/HOOKS_DEVELOPMENT.md) | Creating and maintaining validation hooks |
| [System Guide](./guides/SYSTEM_GUIDE.md) | Original system guide with operational details |
| [Batch Processing](./guides/BATCH_PROCESSING.md) | Running batch validation for all managers |

### API

| Document | Description |
|----------|-------------|
| [API Reference](./api/API_REFERENCE.md) | REST API endpoints, request/response formats |

### Reference

| Document | Description |
|----------|-------------|
| [Legacy Files Reference](./reference/LEGACY_FILES_REFERENCE.md) | Reference to original working files for debugging |

---

## Quick Links

### Getting Started

1. [Prerequisites](./guides/DEVELOPMENT.md#prerequisites)
2. [Initial Setup](./guides/DEVELOPMENT.md#initial-setup)
3. [Running the Application](./guides/DEVELOPMENT.md#running-the-application)

### Creating Hooks

1. [Hook Architecture](./guides/HOOKS_DEVELOPMENT.md#hook-architecture)
2. [BaseHook Class](./guides/HOOKS_DEVELOPMENT.md#basehook-class)
3. [Creating a Check](./guides/HOOKS_DEVELOPMENT.md#creating-a-check)
4. [Configuration](./guides/HOOKS_DEVELOPMENT.md#configuration)

### API Usage

1. [Health Endpoints](./api/API_REFERENCE.md#health)
2. [Hooks Endpoints](./api/API_REFERENCE.md#hooks)
3. [Jobs Endpoints](./api/API_REFERENCE.md#jobs)
4. [Managers Endpoints](./api/API_REFERENCE.md#managers)

---

## Hooks Overview

| Hook | Status | Description | Docs |
|------|--------|-------------|------|
| Monthly Report | **Active** | Monthly fund holdings validation | [Details](./SYSTEM_DOCUMENTATION.md#3-hook-1-monthly-report-validation) |
| Special Transactions | **Development** | Coordinated trades validation | [Details](./SYSTEM_DOCUMENTATION.md#4-hook-2-special-transactions-validation) |
| Financial Report | Specification | Q1 2026 planned | - |

---

## Fund Managers

| Hebrew | English | ID |
|--------|---------|-----|
| מגדל | Migdal | 10040 |
| איילון | Ayalon | 10054 |
| קסם | Kesem | 10047 |
| סיגמא | Sigma | 10048 |
| פורסט | Forest | 10082 |
| הראל | Harel | 10031 |
| אנליסט | Analyst | 10019 |
| מיטב | Meitav | 10083 |
| איביאי | IBI | 10068 |
| אלטשולר-שחם | Altshuler Shaham | 10017 |

---

## Project Structure

```
docs/
├── README.md                    # This file (Documentation Register)
├── SYSTEM_DOCUMENTATION.md      # Complete system overview
├── ARCHITECTURE.md              # Monorepo architecture plan
├── CHEATSHEET.md                # Quick reference
│
├── guides/
│   ├── DEVELOPMENT.md           # Development setup
│   ├── HOOKS_DEVELOPMENT.md     # Hooks guide
│   ├── SYSTEM_GUIDE.md          # Operations guide
│   └── BATCH_PROCESSING.md      # Batch processing
│
├── api/
│   └── API_REFERENCE.md         # API documentation
│
└── reference/
    └── LEGACY_FILES_REFERENCE.md # Original file references
```

---

## External Resources

- **GitHub Repository**: https://github.com/idan82labs/Mizrahi-Platfrom
- **Production API**: https://209.38.226.220.nip.io
- **n8n Workflows**: https://n8n.82labs.io

---

## Support

For questions or issues:
- Open a GitHub issue
- Contact: elay.g@82labs.io
