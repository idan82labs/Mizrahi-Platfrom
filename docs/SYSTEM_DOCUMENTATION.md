# Mizrahi Fund Automation System - Complete Documentation

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Backup Location**: `/home/alexandr/remote_backup/`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Hook #1: Monthly Report Validation](#3-hook-1-monthly-report-validation)
4. [Hook #2: Special Transactions Validation](#4-hook-2-special-transactions-validation)
5. [Frontend Application](#5-frontend-application)
6. [n8n Workflows](#6-n8n-workflows)
7. [Code Version Analysis](#7-code-version-analysis)
8. [Deployment Architecture](#8-deployment-architecture)
9. [File Inventory](#9-file-inventory)
10. [API Reference](#10-api-reference)
11. [Configuration & Credentials](#11-configuration--credentials)

---

## 1. Executive Summary

### What is this system?

The **Mizrahi Fund Automation System** is a production-grade regulatory compliance validation platform for Israeli mutual funds managed by **Mizrahi Tefachot** trustee. It automates the validation of fund reports and special transactions, reducing manual work and improving accuracy.

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Hook #1** | Monthly Report Validation | Python + n8n |
| **Hook #2** | Special Transactions Validation | Python + FastAPI |
| **Frontend** | User Portal | React + Vite + TypeScript |
| **n8n Workflows** | Orchestration & Scheduling | n8n automation platform |
| **Backend API** | Report Processing | FastAPI + Uvicorn |

### Fund Managers Supported (10 total)

| Hebrew Name | English | Item ID |
|-------------|---------|---------|
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

## 2. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐    ┌──────────────────────────────────┐   │
│  │  Frontend Portal         │    │  n8n Form Interface              │   │
│  │  (Vercel)                │    │  (n8n.82labs.io)                 │   │
│  │  mizrahi-smart-tools-    │    │  /form/fund-form                 │   │
│  │  portal.vercel.app       │    │  /form/mizrahi-special-          │   │
│  └───────────┬──────────────┘    │  transactions                    │   │
│              │                    └────────────┬─────────────────────┘   │
└──────────────┼─────────────────────────────────┼─────────────────────────┘
               │ HTTPS                           │ Internal
               ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVICES                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐    ┌──────────────────────────────────┐   │
│  │  Production API Server   │    │  n8n Automation Server           │   │
│  │  209.38.226.220.nip.io   │    │  n8n.82labs.io                   │   │
│  │  ├── Nginx (443)         │    │  ├── Schedule Triggers           │   │
│  │  └── Uvicorn (8000)      │    │  ├── Form Triggers               │   │
│  │      └── FastAPI         │    │  └── Workflow Orchestration      │   │
│  │          └── server.py   │    └────────────┬─────────────────────┘   │
│  └───────────┬──────────────┘                 │                         │
│              │                                 │                         │
│  ┌───────────▼──────────────┐    ┌────────────▼─────────────────────┐   │
│  │  Hook #2 Engine          │    │  Hook #1 Engine                  │   │
│  │  mizrahi_special_        │    │  fund_automation_complete.py     │   │
│  │  transactions.py         │    │  (984 lines)                     │   │
│  │  (2,469 lines)           │    │                                  │   │
│  └───────────┬──────────────┘    └────────────┬─────────────────────┘   │
└──────────────┼─────────────────────────────────┼─────────────────────────┘
               │                                 │
               ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────┐ │
│  │  Apify Actors  │  │  TASE Maya     │  │  Email Services            │ │
│  │  K9WppTziYC3n  │  │  maya.tase.    │  │  ├── Resend API            │ │
│  │  (Funds List)  │  │  co.il         │  │  │   (Production)          │ │
│  │  5lhI6O39Qbgv  │  │  (Data Source) │  │  └── Gmail SMTP            │ │
│  │  (Reports)     │  │                │  │      (Development)         │ │
│  └────────────────┘  └────────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. TRIGGER
   ├── Schedule (n8n cron: 5th of month @ 09:00)
   ├── Manual Form (n8n form or frontend)
   └── API Call (frontend to backend)

2. DATA ACQUISITION
   ├── Apify Actor K9WppTziYC3n2vxTu → Mutual Funds List (XLSX)
   └── Apify Actor 5lhI6O39Qbgv9O0gs → Manager Reports (CSV)

3. PROCESSING
   ├── Hook #1: 7 validation checks on monthly holdings
   └── Hook #2: 7 validation checks on special transactions

4. OUTPUT
   ├── Excel Report (multi-sheet with findings)
   └── Email Notification (HTML + attachment)
```

---

## 3. Hook #1: Monthly Report Validation

### Overview

| Property | Value |
|----------|-------|
| **Hebrew Name** | בקרה אוטומטית על דוח חודשי |
| **Status** | Active (פעיל) |
| **Schedule** | 5th of every month at 09:00 |
| **Main Script** | `fund_automation_complete.py` |
| **Lines of Code** | 984 |
| **n8n Workflow** | `Funds Report Agent Processor.json` |

### Purpose

Validates monthly fund holdings reports by:
- Cross-referencing funds between Magna list and Manager reports
- Identifying unusual asset types
- Detecting new assets and quantity changes
- Checking regulatory compliance (Clauses 214, 328)
- Validating price reasonableness

### Validation Checks (7 total)

| Check | Hebrew Name | Description | Threshold |
|-------|-------------|-------------|-----------|
| 1 | בדיקת שלמות | Cross-reference Magna vs Manager reports | - |
| 2 | סוגי נכסים חריגים | Flag unusual asset types with value > 0 | Types: 16,21,22,23,24,52,53,57,58,99,101,112,201,207,209 |
| 3 | נכסים חדשים | New assets added since previous month | - |
| 4 | שינויים בכמות | Unusual quantity changes month-over-month | - |
| 5 | סעיף 328 | Borrowed quantity consistency check | - |
| 6 | שילובים נדרשים | Required asset type combinations (incl. Clause 214) | See rules below |
| 7 | סבירות מחירים | Price ratio validation | 7.5% variance |

### Required Asset Combinations (Check 6)

```python
REQUIRED_COMBINATIONS = {
    111: [38, 42, 45, 47, 49, 56],  # If any of these >= 100,000 ILS, need type 111
    212: [326, 327],                 # If 326 or 327 exists, need 212
    213: [319],                      # If 319 exists, need 213
    208: [307],                      # If 307 exists, need 208
    210: [310],                      # If 310 exists, need 210
}
```

### Process Flow

```
┌─────────────────────────────────────────────┐
│  n8n Schedule Trigger                       │
│  (5th of month, 09:00 Israel time)          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Apify: Fetch Mutual Funds List             │
│  Actor: K9WppTziYC3n2vxTu                   │
│  Output: Mutual_Funds_List.xlsx             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Apify: Fetch Manager Reports               │
│  Actor: 5lhI6O39Qbgv9O0gs                   │
│  Output: current_month.csv, previous_month.csv │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Python: fund_automation_complete.py        │
│  - Run 7 validation checks                  │
│  - Generate ProcessingResult object         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Generate Excel Report                      │
│  Sheets: סיכום, סטטוס בדיקות, קרנות חסרות,  │
│  נכסים חריגים, נכסים חדשים, שינויים בכמות,  │
│  סעיף 328, שילובים נדרשים, סבירות מחירים    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Gmail: Send Email with Attachment          │
│  To: Control team                           │
└─────────────────────────────────────────────┘
```

### Output Excel Structure

Each sheet includes columns for manual review:
- `האם תקין?` (Is OK?) - for marking reviewed items
- `שם הבודק` (Checker Name) - for audit trail

---

## 4. Hook #2: Special Transactions Validation

### Overview

| Property | Value |
|----------|-------|
| **Hebrew Name** | בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה |
| **Status** | In Development (בפיתוח) |
| **Schedule** | Not active (planned: 5th @ 10:00) |
| **Main Script** | `mizrahi_special_transactions.py` |
| **Batch Script** | `batch_special_transactions.py` |
| **Lines of Code** | 2,469 + 493 = 2,962 total |
| **n8n Workflow** | `mizrahi_special_transactions_workflow.json` |

### Purpose

Validates special transactions (coordinated/off-exchange trades) by:
- Identifying inter-fund transactions (buy/sell pairs)
- Validating transaction dates within report month
- Checking decision method compliance (דחצ voting)
- Cross-checking prices with TASE market data
- Flagging problematic securities

### Validation Checks (7 total)

| Check | Name | Description |
|-------|------|-------------|
| CHK_1 | Duplicates | Inter-fund transactions (buy/sell pairs with matching security, date, quantity) |
| CHK_2 | Fund Scope | Filter to Mizrahi-trusteed funds only |
| CHK_3 | Date Validation | Transaction dates must fall within report month |
| CHK_4 | Decision Method | Validate decision method codes (1 or 2) and דחצ voting rules |
| CHK_5 | Sampling | Random samples for manual verification |
| CHK_6 | TASE Prices | Cross-check transaction prices with TASE market data (optional, Selenium-based) |
| CHK_7 | Problematic Securities | Flag securities on warning/halt/restricted lists |

### Decision Method Rules (Check 4)

```python
# Transaction types requiring decision method 1
TYPE_REQUIRES_DECISION_1 = {12, 22}

# Transaction types requiring decision method 1 or 2
TYPE_REQUIRES_DECISION_1_OR_2 = {31, 32, 33, 34, 35, 36}

# דחצ (External Director) Voting Rules:
# Rule 4ג: If decision method = 1, at least one דחצ must have vote = 1
# Rule 4ד: If any דחצ has vote = 2, flag for review (potential issue)
```

### Process Flow (Manual/API Triggered)

```
┌─────────────────────────────────────────────┐
│  TRIGGER OPTIONS:                           │
│  ├── Frontend form submission               │
│  ├── n8n form (/mizrahi-special-transactions)│
│  └── Direct API call                        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  POST /api/process-report                   │
│  Form Data:                                 │
│  - manager_name: "סיגמא"                    │
│  - email: "user@example.com"                │
│  - price_threshold: 5.0 (optional)          │
│  - skip_tase_prices: true (optional)        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Backend: Download from TASE Maya via Apify │
│  - Mutual Funds List                        │
│  - Special Transactions Report              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Python: mizrahi_special_transactions.py    │
│  - Parse transaction data                   │
│  - Run 7 validation checks                  │
│  - Generate Excel report                    │
│  - Build email JSON                         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Resend API: Send Email                     │
│  - Main report with Excel attachment        │
│  - Samples forward email (optional)         │
└─────────────────────────────────────────────┘
```

### Output Excel Structure

| Sheet | Content |
|-------|---------|
| סיכום (Summary) | Overview statistics |
| סטטוס בדיקות (Check Statuses) | Pass/fail for each validation |
| עסקאות כפולות (Duplicates) | Inter-fund transactions |
| חריגות תאריך (Date Exceptions) | Transactions outside report month |
| חריגות החלטה (Decision Exceptions) | Invalid decision methods |
| דגימות (Samples) | Random samples for verification |
| בדיקות מחיר (Price Checks) | TASE price variance analysis |
| ניירות בעייתיים (Problematic Securities) | Flagged securities |
| מחוץ לטווח (Out of Scope) | Non-Mizrahi funds |

---

## 5. Frontend Application

### Overview

| Property | Value |
|----------|-------|
| **Repository** | `mizrahi-smart-tools-portal` |
| **Deployment** | Vercel |
| **URL** | https://mizrahi-smart-tools-portal.vercel.app |
| **Framework** | React 18 + TypeScript + Vite |
| **UI Library** | Tailwind CSS + shadcn/ui + Radix UI |
| **State Management** | TanStack Query |

### Technology Stack

```json
{
  "framework": "React 18.3.1",
  "build": "Vite 5.4.19",
  "language": "TypeScript 5.8.3",
  "styling": "Tailwind CSS 3.4.17",
  "components": "shadcn/ui + Radix UI",
  "routing": "react-router-dom 6.30.1",
  "forms": "react-hook-form 7.61.1 + zod 3.25.76",
  "charts": "recharts 2.15.4"
}
```

### Application Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Index.tsx` | Homepage with tool cards |
| `/tool-monthly` | `ToolMonthly.tsx` | Hook #1 details & manual run |
| `/tool-matched` | `ToolMatched.tsx` | Hook #2 details & manual run |
| `/tool-financial` | `ToolFinancial.tsx` | Future tool (Q1 2026) |
| `*` | `NotFound.tsx` | 404 page |

### Key Components

```
src/
├── App.tsx                 # Main router configuration
├── main.tsx               # Application entry point
├── pages/
│   ├── Index.tsx          # Homepage with 5 tool cards
│   ├── ToolMonthly.tsx    # Hook #1 page (links to n8n form)
│   ├── ToolMatched.tsx    # Hook #2 page (direct API integration)
│   ├── ToolFinancial.tsx  # Placeholder for future tool
│   └── NotFound.tsx       # 404 page
├── components/
│   ├── TopBar.tsx         # Navigation header
│   ├── Footer.tsx         # Footer with 82Labs branding
│   ├── ToolCard.tsx       # Tool card component
│   ├── StatusBadge.tsx    # Active/Development/Specification badges
│   ├── CheckTable.tsx     # Validation checks table
│   └── ui/                # shadcn/ui components (50+ files)
└── assets/
    ├── logo.svg           # Mizrahi Tefachot logo
    ├── monthly-report-example.png
    └── matched-report-example.png
```

### Tools Displayed on Homepage

| Tool | Status | Auto-Run |
|------|--------|----------|
| בקרה אוטומטית על דוח חודשי | Active | 5th @ 09:00 |
| בקרה אוטומטית על דוח עסקאות מתואמות | Development | Not active |
| בדיקת דוח כספי אוטומטית | Specification | Q1 2026 |
| אוטומציית בדיקת דמי ניהול משתנים | Specification | Q1 2026 |
| אוטומציית דוח גילוי נאות ק.303 | Specification | Q1 2026 |

### API Integration (ToolMatched.tsx)

The frontend directly integrates with the production API for Hook #2:

```typescript
const API_BASE = "https://209.38.226.220.nip.io";

// Submit report request
const response = await fetch(`${API_BASE}/api/process-report`, {
  method: "POST",
  body: formData,  // manager_name, email
});
const { job_id } = await response.json();

// Poll for completion
const status = await fetch(`${API_BASE}/api/job/${job_id}`);
// Statuses: queued → downloading → processing → sending_email → completed
```

---

## 6. n8n Workflows

### Workflow #1: Funds Report Agent Processor (Hook #1)

**File**: `Funds Report Agent Processor.json`

| Property | Value |
|----------|-------|
| **ID** | y06oR8jGKE6VBrBs |
| **Trigger** | `executeWorkflowTrigger` (called by parent workflow) |
| **Active** | true |
| **Purpose** | Process monthly fund reports |

#### Workflow Nodes

```
Start (executeWorkflowTrigger)
    │ Inputs: emails, fundCode, fundName
    ▼
Create Download Link (code)
    │ Builds Maya URL with date range
    ▼
Mutual Funds Main Report Downloader (Apify)
    │ Actor: K9WppTziYC3n2vxTu
    ▼
Funds Manager Actor (Apify)
    │ Actor: 5lhI6O39Qbgv9O0gs
    │ Downloads report from Maya URL
    ▼
Funds Manager Actor - Get DB (Apify)
    │ Gets dataset items
    ▼
[Disabled] Latest Month Downloader
[Disabled] Previous Month Downloader
    ▼
HTML Parser (html)
    │ Generates email HTML template
    ▼
Fetch From Server - JS (code)
    │ Calls Python server at http://209.38.226.220/process
    │ Sends multipart form with files
    ▼
Send a message (Gmail)
    │ Sends email with Excel attachment
```

### Workflow #2: Mizrahi Special Transactions Orchestrator (Hook #2)

**File**: `mizrahi_special_transactions_workflow.json`

| Property | Value |
|----------|-------|
| **Trigger** | `formTrigger` (manual form submission) |
| **Path** | `/mizrahi-special-transactions` |
| **Purpose** | Process special transactions reports |

#### Workflow Nodes

```
Form Trigger - Upload Files
    │ Fields: Manager Name, Email, Files, Price Threshold
    ▼
Extract Form Data (set)
    │ Extracts managerName, emails, priceThreshold, etc.
    ▼
Create Input/Output Dirs (SSH)
    │ mkdir -p /root/input /root/output
    ▼
Upload Files (SSH × 3, parallel)
    │ ├── Upload Mutual Funds List
    │ ├── Upload Manager Report
    │ └── Upload Spec File (Optional)
    ▼
Merge After Upload (merge)
    ▼
Run Special Transactions Script (SSH)
    │ python3 mizrahi_special_transactions.py [args]
    ▼
Get Output Excel Path + Get Email JSON (parallel)
    ▼
Download Output Excel (SSH)
    ▼
Process Output Data (code)
    ▼
Generate Email HTML (html)
    ▼
Send Report Email (Gmail)
    ▼
Cleanup Input Files (SSH)

Error Handling:
Error Trigger → Send Error Email
```

---

## 7. Code Version Analysis

### Summary: Latest Versions

| File | Latest Location | Evidence |
|------|-----------------|----------|
| `fund_automation_complete.py` | **ROOT** | Only copy exists |
| `mizrahi_special_transactions.py` | **ROOT** | Largest size (105,578 bytes), most features |
| `batch_special_transactions.py` | **ROOT** | Correct event ID (5618) |
| `test_special_transactions_all_managers.py` | **ROOT** | Correct event ID (5618) |
| `send_batch_email.py` | Either | Identical in ROOT and Mizrahi-Automations |
| `send_test_results.py` | Either | Identical in ROOT and Mizrahi-Automations |

### Detailed Version Comparison

#### `mizrahi_special_transactions.py`

| Location | Size | Lines | MD5 (first 8) | Status |
|----------|------|-------|---------------|--------|
| **ROOT** | 105,578 | 2,469 | 3ad16588 | **LATEST** |
| Mizrahi-Automations | 94,903 | 2,239 | c68ff4f6 | Older |
| mizrahi-test-env | 105,578 | 2,469 | 3ad16588 | = ROOT |

**Why ROOT is latest:**
1. **230 more lines** of code
2. **New validation functions** not in Mizrahi-Automations:
   - `check_4g_dachatz_vote_required()` - דחצ vote=1 required check
   - `check_4d_dachatz_vote_2_flag()` - דחצ vote=2 flag check
   - `check_6g_internal_price_discrepancy()` - Internal price comparison
3. **New loggers**: `logger_chk4_dachatz`, `logger_chk6_internal`
4. **New TxnRow properties**: `dachatz_votes`, `has_any_dachatz_vote_1`, `has_any_dachatz_vote_2`
5. **Cleaner code**: Removed Windows UTF-8 wrapper

#### `batch_special_transactions.py`

| Location | Event ID | Size | Status |
|----------|----------|------|--------|
| **ROOT** | **5618** ✓ | 16,588 | **LATEST** |
| Mizrahi-Automations | 5615 ✗ | 16,968 | Older (wrong event ID) |
| mizrahi-test-env | 5615 ✗ | 17,468 | Test fork |

**Why ROOT is latest:**
1. **Correct event ID** (5618 for special transactions)
2. Removed UTF-8 wrapper
3. Spec file is optional (not required default)

#### Git History (Mizrahi-Automations)

```
dfda036  2026-01-15  Security: Move TASE API key to environment variable
ea8d6e1  ...         Update CHK_1, CHK_4, and CHK_5 validation logic
66516d8  ...         Add דחצ (decision criteria) validation to CHK_4
7d43adf  ...         Add spec file, tests folder, and improve log organization
e295b2d  ...         Fix event ID and update email structure
7e20615  ...         Initial commit
```

The ROOT version contains changes **after** the last git commit (2026-01-15).

---

## 8. Deployment Architecture

### Production Server

| Property | Value |
|----------|-------|
| **IP Address** | 209.38.226.220 |
| **Domain** | 209.38.226.220.nip.io (wildcard DNS) |
| **OS** | Linux |
| **SSL** | Let's Encrypt (auto-renewal via certbot) |

### Service Stack

```
┌─────────────────────────────────────────┐
│  Nginx (ports 80, 443)                  │
│  - SSL termination                      │
│  - Reverse proxy to localhost:8000      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Uvicorn (port 8000)                    │
│  - ASGI server                          │
│  - Managed by systemd (mizrahi-api)     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  FastAPI Application                    │
│  - /opt/mizrahi/server.py               │
│  - Imports mizrahi_special_transactions │
└─────────────────────────────────────────┘
```

### File Locations on Server

| Location | Purpose |
|----------|---------|
| `/opt/mizrahi/` | Production deployment |
| `/root/` | Development workspace (git repo) |
| `/root/mizrahi-venv/` | Python virtual environment |
| `/etc/nginx/sites-enabled/` | Nginx configuration |
| `/etc/letsencrypt/` | SSL certificates |

### Systemd Service

```bash
# Check status
sudo systemctl status mizrahi-api

# Restart
sudo systemctl restart mizrahi-api

# View logs
sudo journalctl -u mizrahi-api -f
```

### Frontend Deployment (Vercel)

| Property | Value |
|----------|-------|
| **Platform** | Vercel |
| **URL** | https://mizrahi-smart-tools-portal.vercel.app |
| **Build Command** | `vite build` |
| **Framework** | Vite + React |
| **Auto Deploy** | Yes (on git push) |

### n8n Server

| Property | Value |
|----------|-------|
| **URL** | https://n8n.82labs.io |
| **Form URLs** | `/form/fund-form`, `/form/mizrahi-special-transactions` |
| **Credentials** | Gmail OAuth2 (Elay.g), Apify API |

---

## 9. File Inventory

### Root Directory (`/home/alexandr/remote_backup/`)

| File/Directory | Type | Size | Purpose |
|----------------|------|------|---------|
| `fund_automation_complete.py` | Python | 41 KB | **Hook #1** main script |
| `mizrahi_special_transactions.py` | Python | 106 KB | **Hook #2** main script (LATEST) |
| `batch_special_transactions.py` | Python | 17 KB | Batch processor (LATEST) |
| `test_special_transactions_all_managers.py` | Python | 14 KB | Test harness |
| `send_batch_email.py` | Python | 5 KB | Gmail email sender |
| `send_test_results.py` | Python | 3 KB | Test results emailer |
| `run_batch_all.sh` | Shell | 3 KB | Batch processing script |
| `run_batch_test.sh` | Shell | 1 KB | Single manager test script |
| `mizrahi_special_transactions_workflow.json` | JSON | 29 KB | n8n workflow (Hook #2) |
| `Funds Report Agent Processor.json` | JSON | 22 KB | n8n workflow (Hook #1) |
| `README.md` | Markdown | 7 KB | Quick start guide |
| `SYSTEM_GUIDE.md` | Markdown | 19 KB | Architecture documentation |
| `BATCH_PROCESSING_README.md` | Markdown | 6 KB | Batch processing guide |
| `CHEATSHEET.md` | Markdown | 3 KB | Quick reference |
| `Mizrahi-Automations/` | Directory | 264 KB | Git repo backup (older versions) |
| `mizrahi-test-env/` | Directory | 2 MB | Test environment |
| `mizrahi-smart-tools-portal/` | Directory | - | Frontend application |
| `batch_output/` | Directory | 18 MB | Batch processing results |
| `output/` | Directory | 144 KB | Individual outputs |
| `log/` | Directory | 40 KB | Processing logs |

### Frontend Directory (`mizrahi-smart-tools-portal/`)

| File/Directory | Purpose |
|----------------|---------|
| `package.json` | Dependencies and scripts |
| `vite.config.ts` | Vite configuration |
| `tailwind.config.ts` | Tailwind CSS configuration |
| `tsconfig.json` | TypeScript configuration |
| `src/App.tsx` | Main application with routing |
| `src/pages/` | Page components (4 pages) |
| `src/components/` | Reusable components |
| `src/components/ui/` | shadcn/ui components (50+ files) |
| `src/assets/` | Images and logos |

---

## 10. API Reference

### Production API (209.38.226.220.nip.io)

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "Mizrahi Special Transactions API",
  "version": "3.0.0"
}
```

#### `GET /api/managers`
List available fund managers.

**Response:**
```json
{
  "managers": [
    {"name": "מגדל", "item_id": "10040"},
    {"name": "איילון", "item_id": "10054"},
    ...
  ]
}
```

#### `POST /api/process-report`
Process special transactions report.

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `manager_name` | string | Yes | Hebrew name (e.g., "סיגמא") |
| `email` | string | Yes | Recipient(s), semicolon-separated |
| `price_threshold` | float | No | Price variance % (default: 5.0) |
| `skip_tase_prices` | boolean | No | Skip TASE scraping (default: true) |

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "Processing started"
}
```

#### `GET /api/job/{job_id}`
Check job status.

**Response:**
```json
{
  "status": "processing",  // queued, downloading, processing, sending_email, completed, failed
  "message": "Processing report...",
  "result": {  // Only when completed
    "summary": {...},
    "email_sent_to": ["user@example.com"],
    "output_file": "report.xlsx"
  }
}
```

#### `GET /api/download/{filename}`
Download generated report file.

---

## 11. Configuration & Credentials

### API Keys

| Service | Key | Purpose |
|---------|-----|---------|
| Apify | `<REDACTED_APIFY_TOKEN>` | Web scraping actors |
| Resend | `<REDACTED_RESEND_KEY>` | Email delivery (production) |

### Apify Actor IDs

| Actor | ID | Purpose |
|-------|-----|---------|
| Funds List | `K9WppTziYC3n2vxTu` | Download Mutual Funds List from Maya |
| Reports | `5lhI6O39Qbgv9O0gs` | Download fund reports from Maya |

### Email Configuration

**Production (Resend API):**
```
FROM_EMAIL: notifications@82labs.io
API_KEY: <REDACTED_RESEND_KEY>
```

**Development (Gmail SMTP):**
```
SMTP Server: smtp.gmail.com:465 (SSL)
Requires: Gmail App Password + 2FA enabled
```

### Environment Variables

```bash
RESEND_API_KEY=<REDACTED_RESEND_KEY>
APIFY_API_TOKEN=<REDACTED_APIFY_TOKEN>
FROM_EMAIL=notifications@82labs.io
```

---

## Appendix A: Troubleshooting

### Common Issues

1. **Server not responding**
   ```bash
   sudo systemctl restart mizrahi-api
   sudo journalctl -u mizrahi-api -n 100
   ```

2. **SSL certificate issues**
   ```bash
   sudo certbot renew
   sudo systemctl restart nginx
   ```

3. **Apify actor fails**
   - Check API token validity
   - Verify Maya URL format
   - Check event ID (should be 5618 for special transactions)

4. **Email not sending**
   - Resend: Check API key and "from" email authorization
   - Gmail: Use App Password, ensure 2FA enabled

---

## Appendix B: Development Workflow

### Updating Production Code

```bash
# On server
cd /root
git pull

# Copy to production
sudo cp mizrahi_special_transactions.py /opt/mizrahi/
sudo cp server.py /opt/mizrahi/

# Restart
sudo systemctl restart mizrahi-api
```

### Running Batch Processing

```bash
# Activate environment
source /root/mizrahi-venv/bin/activate

# Run for all managers
./run_batch_all.sh YOUR_APIFY_TOKEN [GMAIL_USER] [GMAIL_PASSWORD]

# Run for single manager (test)
./run_batch_test.sh YOUR_APIFY_TOKEN
```

---

**Document End**

*Generated by Claude Code analysis of backup at `/home/alexandr/remote_backup/`*
