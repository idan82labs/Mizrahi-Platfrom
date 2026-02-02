# Mizrahi Compliance Platform Documentation

Welcome to the documentation for the Mizrahi Compliance Platform.

---

## Documentation Index

### Overview

| Document | Description |
|----------|-------------|
| [System Documentation](./SYSTEM_DOCUMENTATION.md) | Complete system overview, architecture, and component details |
| [Architecture Plan](./ARCHITECTURE.md) | Monorepo architecture design and implementation plan |
| [Cheatsheet](./CHEATSHEET.md) | Quick reference commands and common operations |

---

### Guides

| Document | Description |
|----------|-------------|
| [Development Guide](./guides/DEVELOPMENT.md) | Setting up development environment, coding standards |
| [Hooks Development](./guides/HOOKS_DEVELOPMENT.md) | Creating and maintaining validation hooks |
| [System Guide](./guides/SYSTEM_GUIDE.md) | Original system guide with operational details |
| [Batch Processing](./guides/BATCH_PROCESSING.md) | Running batch validation for all managers |

---

### API

| Document | Description |
|----------|-------------|
| [API Reference](./api/API_REFERENCE.md) | REST API endpoints, request/response formats |

---

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

## Project Structure

```
docs/
├── README.md                    # This file
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

## Hooks Overview

| Hook | Status | Description |
|------|--------|-------------|
| [Monthly Report](./SYSTEM_DOCUMENTATION.md#3-hook-1-monthly-report-validation) | Active | Monthly fund holdings validation |
| [Special Transactions](./SYSTEM_DOCUMENTATION.md#4-hook-2-special-transactions-validation) | Development | Coordinated trades validation |
| Financial Report | Specification | Q1 2026 planned |

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
