# Mizrahi Compliance Platform - Architecture

**Document Version**: 1.0 **Created**: 2026-02-02 **Status**: Planning Phase

---

## Overview

This directory contains the architecture documentation for the Mizrahi
Compliance Platform monorepo.

## Documents

| Document                                                | Description                                                 |
| ------------------------------------------------------- | ----------------------------------------------------------- |
| [Overview](./OVERVIEW.md)                               | Executive summary, current state analysis, requirements     |
| [System Design](./SYSTEM_DESIGN.md)                     | High-level architecture and directory structure             |
| [Hook System](./HOOK_SYSTEM.md)                         | Hook plugin system, BaseHook class, registry                |
| [Configuration](./CONFIGURATION.md)                     | YAML configuration format for hooks, managers, environments |
| [API Design](./API_DESIGN.md)                           | RESTful API endpoints and TypeScript types                  |
| [Deployment](./DEPLOYMENT.md)                           | Hosting recommendations and Docker setup                    |
| [Additional Requirements](./ADDITIONAL_REQUIREMENTS.md) | Job history, SSE, notifications, health checks              |
| [Migration Plan](./MIGRATION_PLAN.md)                   | Phased migration timeline                                   |
| [Technical Decisions](./TECHNICAL_DECISIONS.md)         | Technology choices and appendices                           |

## Quick Navigation

### By Role

**Developers:**

- Start with [Overview](./OVERVIEW.md) for context
- Read [System Design](./SYSTEM_DESIGN.md) for structure
- See [Hook System](./HOOK_SYSTEM.md) for creating hooks

**DevOps:**

- [Deployment](./DEPLOYMENT.md) for hosting setup
- [Additional Requirements](./ADDITIONAL_REQUIREMENTS.md) for monitoring

**Project Managers:**

- [Overview](./OVERVIEW.md) for goals and requirements
- [Migration Plan](./MIGRATION_PLAN.md) for timeline

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

_See individual documents for detailed information._
