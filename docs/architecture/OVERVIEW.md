# Architecture Overview

This document covers the executive summary, current state analysis, and
requirements for the Mizrahi Compliance Platform.

**Related Documents:**

- [System Design](./SYSTEM_DESIGN.md) - Proposed architecture
- [Migration Plan](./MIGRATION_PLAN.md) - Implementation timeline

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Requirements](#requirements)

---

## Executive Summary

### Goal

Transform the current scattered Mizrahi Fund Automation System into a unified
**monorepo** with:

- Single codebase for all components
- Plugin-based hook architecture for easy extensibility
- Unified hosting platform
- Configuration-driven schedules and parameters

### Key Outcomes

| Outcome                     | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| **Centralized Development** | All code in one repository with shared tooling         |
| **Simplified Operations**   | Single deployment target instead of 3 separate systems |
| **Extensible Architecture** | Add new hooks by creating a directory and registering  |
| **Configuration-Driven**    | Change schedules and parameters without code changes   |
| **Audit Trail**             | Full job history with database persistence             |

---

## Current State Analysis

### Current Architecture Problems

| Component         | Current State                                  | Problem                                                       |
| ----------------- | ---------------------------------------------- | ------------------------------------------------------------- |
| **Code Location** | Files scattered across multiple directories    | Duplicate code in 6+ places, version confusion                |
| **Frontend**      | Vercel (mizrahi-smart-tools-portal.vercel.app) | Separate deployment, links to n8n forms                       |
| **Backend**       | VPS at 209.38.226.220                          | Manual deployment, no CI/CD                                   |
| **Orchestration** | n8n at n8n.82labs.io                           | Third system to maintain, workflow changes require n8n access |
| **Configuration** | Hardcoded in Python scripts                    | Changes require code deployment                               |
| **Job History**   | None                                           | No audit trail, no debugging history                          |

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

| Metric                                   | Value    |
| ---------------------------------------- | -------- |
| Total Python files                       | 14       |
| Total Frontend files                     | 70+      |
| Lines in mizrahi_special_transactions.py | 2,469    |
| Lines in fund_automation_complete.py     | 984      |
| Lines in batch_special_transactions.py   | 493      |
| Duplicated constant definitions          | 6 places |

---

## Requirements

### Primary Requirements (User-Specified)

| ID  | Requirement                                                      | Priority |
| --- | ---------------------------------------------------------------- | -------- |
| R1  | Centralized repository for easy change tracking and debugging    | High     |
| R2  | Single hosting service to simplify maintenance                   | High     |
| R3  | Frontend for manual hook triggering and intermediate data access | High     |
| R4  | Easy implementation of new hooks into existing workflow          | High     |
| R5  | Configurable schedules with proper config format                 | High     |

### Derived Requirements

| ID  | Requirement                         | Rationale                   |
| --- | ----------------------------------- | --------------------------- |
| R6  | Job history and audit logging       | Compliance, debugging       |
| R7  | Real-time progress updates          | UX improvement              |
| R8  | Environment-based configuration     | Dev/staging/prod separation |
| R9  | Health checks and monitoring        | Operational visibility      |
| R10 | Rate limiting for external services | Prevent API abuse           |
| R11 | Comprehensive test infrastructure   | Quality assurance           |
| R12 | Notification system (email + Slack) | Team awareness              |

---

**Next:** [System Design](./SYSTEM_DESIGN.md)
