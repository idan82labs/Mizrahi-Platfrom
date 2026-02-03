# Mizrahi Compliance Platform - Architecture

> **Note:** This document has been split into focused sections for better
> maintainability. See the [architecture/](./architecture/) directory for
> detailed documentation.

---

## Quick Links

| Document                                                             | Description                                                 |
| -------------------------------------------------------------------- | ----------------------------------------------------------- |
| [Overview](./architecture/OVERVIEW.md)                               | Executive summary, current state analysis, requirements     |
| [System Design](./architecture/SYSTEM_DESIGN.md)                     | High-level architecture and directory structure             |
| [Hook System](./architecture/HOOK_SYSTEM.md)                         | Hook plugin system, BaseHook class, registry                |
| [Configuration](./architecture/CONFIGURATION.md)                     | YAML configuration format for hooks, managers, environments |
| [API Design](./architecture/API_DESIGN.md)                           | RESTful API endpoints and TypeScript types                  |
| [Deployment](./architecture/DEPLOYMENT.md)                           | Hosting recommendations and Docker setup                    |
| [Additional Requirements](./architecture/ADDITIONAL_REQUIREMENTS.md) | Job history, SSE, notifications, health checks              |
| [Migration Plan](./architecture/MIGRATION_PLAN.md)                   | Phased migration timeline                                   |
| [Technical Decisions](./architecture/TECHNICAL_DECISIONS.md)         | Technology choices and appendices                           |

---

## Key Goals

Transform the current scattered Mizrahi Fund Automation System into a unified
**monorepo** with:

- Single codebase for all components
- Plugin-based hook architecture for easy extensibility
- Unified hosting platform
- Configuration-driven schedules and parameters

## Key Outcomes

| Outcome                     | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| **Centralized Development** | All code in one repository with shared tooling         |
| **Simplified Operations**   | Single deployment target instead of 3 separate systems |
| **Extensible Architecture** | Add new hooks by creating a directory and registering  |
| **Configuration-Driven**    | Change schedules and parameters without code changes   |
| **Audit Trail**             | Full job history with database persistence             |

---

## Document Index

For the complete architecture documentation, see:

- **[Architecture README](./architecture/README.md)** - Full index and
  navigation guide
