# Mizrahi System Architecture Guide

**Last Updated**: 2026-02-06
**Purpose**: Comprehensive guide for the Mizrahi fund validation and automation system

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Hooks Overview](#hooks-overview)
4. [Email System](#email-system)
5. [Infrastructure](#infrastructure)
6. [Common Operations](#common-operations)
7. [Troubleshooting](#troubleshooting)

---

## System Overview

The Mizrahi system validates regulatory compliance for Israeli mutual funds managed
by Mizrahi Tefachot trustee. It consists of four validation hooks:

1. **Hook 1** - Monthly Report Validation (Maya TASE Event 5618)
2. **Hook 2** - Special Transactions Validation (Maya TASE Event 5615)
3. **Hook 4** - Daily Tracking Validation (TASE Data Hub API)
4. **Hook 5** - K.303 Disclosure Validation (ISA Magna)

All hooks:
- Fetch data from TASE Maya / ISA Magna via Apify actors
- Process and validate according to regulatory rules
- Generate Excel reports with findings
- Send results via Resend email API

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend: mizrahi-smart-tools-portal.vercel.app            │
│  (React + TypeScript + Vite)                                │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS
┌─────────────────▼───────────────────────────────────────────┐
│  209.38.226.220.nip.io (SSL via Let's Encrypt)              │
│  ├── Nginx (ports 80/443)                                   │
│  └── Reverse proxy to localhost:8000                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│  Server: deploy/digitalocean/                               │
│  ├── server.py (FastAPI + Uvicorn on port 8000)             │
│  └── scripts/                                               │
│      ├── hook_utils.py           (shared utilities)         │
│      ├── fund_automation_complete.py  (Hook 1 processor)    │
│      ├── mizrahi_special_transactions.py (Hook 2 processor) │
│      ├── mizrahi_4_logic.py      (Hook 4 processor)         │
│      ├── disclosure_k303_validator.py (Hook 5 processor)    │
│      ├── batch_hook1_with_email.py    (Hook 1 batch)        │
│      ├── batch_hook2_with_email.py    (Hook 2 batch)        │
│      ├── batch_hook5_with_email.py    (Hook 5 batch)        │
│      └── batch_all_hooks.py      (unified batch 1+2+5)      │
└─────────────────────────────────────────────────────────────┘

External Services:
  ├── Apify API (Web scraping Maya TASE / ISA Magna)
  ├── Resend API (Email delivery)
  ├── TASE Maya (Data source for Hook 1, 2, 5)
  └── TASE Data Hub (API for Hook 4)
```

### Key Design Decisions

- **`hook_utils.py`** is the shared module (constants, Apify helpers, email templates, logging)
- All batch scripts import from `hook_utils.py` - no code duplication
- All email delivery via Resend API (no Gmail SMTP)
- All scripts load `.env` via `python-dotenv`
- 8 fund managers configured (centralized in `hook_utils.py`)

---

## Hooks Overview

### Fund Managers (8)

| Hebrew      | English          | ID    |
|-------------|------------------|-------|
| מגדל        | Migdal           | 10040 |
| קסם         | Kesem            | 10047 |
| סיגמא       | Sigma            | 10048 |
| הראל        | Harel            | 10031 |
| אנליסט      | Analyst          | 10019 |
| מיטב        | Meitav           | 10083 |
| איביאי      | IBI              | 10068 |
| אלטשולר-שחם | Altshuler Shaham | 10017 |

### Apify Actors

| Actor ID              | Purpose                                    |
|-----------------------|--------------------------------------------|
| `K9WppTziYC3n2vxTu`  | Download Mutual Funds List from Maya       |
| `5lhI6O39Qbgv9O0gs`  | Download reports from Maya (Hook 1, 2)     |
| `iTpNz9ixbdQCmH43C`  | Download K.303 reports from Magna (Hook 5) |

### Hook 1: Monthly Report (Event 5618)

**Color**: Green (#4a9d7c)
**Batch script**: `batch_hook1_with_email.py`
**Processor**: `fund_automation_complete.py`

Validates monthly fund holdings reports against Magna list.

**Checks:**
1. Fund Completeness - Cross-reference Magna vs Manager reports
2. Unusual Asset Types - Flag non-standard asset types
3. New Assets - Assets added since previous month
4. Quantity Changes - Unusual changes month-over-month
5. Clause 328 - Borrowed quantity consistency
6. Required Combinations - Asset type pairs (Clause 214)
7. Price Reasonableness - Price ratio validation (7.5% threshold)

### Hook 2: Special Transactions (Event 5615)

**Color**: Orange (#F5821F)
**Batch script**: `batch_hook2_with_email.py`
**Processor**: `mizrahi_special_transactions.py`

Validates coordinated and off-exchange trades.

**Checks:**
1. Inter-fund Transactions - Buy/sell pairs detection
2. Date Validation - Dates within report month
3. Decision Method - Decision method rules
4. External Director Voting - Voting rules
5. Sampling - Random samples for verification
6. Price Checks - Price > 100 and internal comparison
7. Problematic Securities - Warning/halt/restricted lists

### Hook 4: Daily Tracking (TASE Data Hub)

**Batch script**: None (standalone CLI)
**Processor**: `mizrahi_4_logic.py`

Validates daily fund tracking data against TASE market data.

**Checks:**
1. NAV tracking against benchmark index
2. BFIX/Bloomberg exchange rate validation
3. Management fee calculation verification
4. Index tracking accuracy (INDX)

**Requires**: `TASE_API_KEY` environment variable (optional, degrades gracefully)

### Hook 5: K.303 Disclosure (ISA Magna)

**Color**: Emerald (#10B981)
**Batch script**: `batch_hook5_with_email.py`
**Processor**: `disclosure_k303_validator.py`

Validates K.303 disclosure reports from ISA Magna.

**Checks:**
1. Check 1a - Fund Completeness
2. Check 1b - Date Validity
3. Check 2a - Previous Month Comparison (>10% threshold)
4. Check 2b - Exposure Profile Validation
5. Checks 3a-3h - Code Combinations (FX, bonds, government/corporate)

---

## API Endpoints

| Endpoint                         | Method | Description                   |
|----------------------------------|--------|-------------------------------|
| `/`                              | GET    | Service info (version 5.0.0)  |
| `/health`                        | GET    | Health check                  |
| `/api/managers`                  | GET    | List fund managers            |
| `/api/process-report`            | POST   | Hook 2 - Special Transactions |
| `/api/process-monthly-report`    | POST   | Hook 1 - Monthly Report       |
| `/api/process-disclosure-report` | POST   | Hook 5 - K.303 Disclosure     |
| `/api/job/{job_id}`              | GET    | Get job status                |
| `/api/download/{filename}`       | GET    | Download generated report     |

---

## Email System

All email delivery uses the **Resend API**. No Gmail SMTP.

```python
# Configuration (from .env)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = "noreply@notifications.82labs.io"
```

### Email Templates

Each hook has a branded HTML email template with:
- Hosted Mizrahi Tefachot logo (PNG on GitHub)
- Color-coded header per hook
- RTL Hebrew layout
- Excel report attached

### Email Types

1. **Report Email** - Per-manager validation results with XLSX attachment
2. **Failure Alert** - Sent when batch processing encounters errors

---

## Environment Variables

| Variable          | Required | Description                               |
|-------------------|----------|-------------------------------------------|
| `APIFY_API_TOKEN` | Yes      | Apify API token for TASE Maya data        |
| `RESEND_API_KEY`  | Yes      | Resend API key for email delivery         |
| `FROM_EMAIL`      | No       | Sender email (default: noreply@notifications.82labs.io) |
| `TASE_API_KEY`    | No       | TASE Data Hub API key (Hook 4 index data) |

Stored in `deploy/digitalocean/.env`, loaded via `python-dotenv`.

---

## Infrastructure

### Server

- **Public IP**: 209.38.226.220
- **Domain**: 209.38.226.220.nip.io (via nip.io wildcard DNS)
- **SSL**: Let's Encrypt (auto-renewal via certbot)
- **Process Manager**: systemd (`mizrahi-api.service`)
- **Reverse Proxy**: Nginx (ports 80/443 -> localhost:8000)

### Systemd Commands

```bash
sudo systemctl start mizrahi-api
sudo systemctl stop mizrahi-api
sudo systemctl restart mizrahi-api
sudo journalctl -u mizrahi-api -f
```

---

## Common Operations

### Run Individual Hooks

```bash
cd deploy/digitalocean

# Hook 1 - Monthly Report
./run_hook1.sh --email "your@email.com"

# Hook 2 - Special Transactions
./run_hook2.sh --email "your@email.com"

# Hook 5 - K.303 Disclosure
./run_hook5.sh --email "your@email.com"

# All hooks for all managers
./run_all_managers.sh --email "your@email.com"
```

### Run Specific Managers

```bash
python scripts/batch_hook1_with_email.py --managers "מגדל,סיגמא" --email "your@email.com"
python scripts/batch_hook2_with_email.py --managers "מגדל,הראל" --email "your@email.com"
python scripts/batch_hook5_with_email.py --managers "מגדל" --email "your@email.com"
```

### Test Hooks

```bash
# Test Hook 1 (requires Apify token)
./test_hook1.sh סיגמא

# Test Hook 2 offline (no Apify needed)
./test_offline_hook2.sh סיגמא

# Test Hook 5 offline (no Apify needed)
./test_offline_hook5.sh מגדל 2025-11

# Test Hook 5 via API (requires running server)
./test_hook5.sh מגדל test@test.com
```

### Check Server Status

```bash
curl https://209.38.226.220.nip.io/health
ps aux | grep uvicorn
sudo journalctl -u mizrahi-api -n 100
```

---

## Troubleshooting

### Server Not Responding

```bash
ps aux | grep uvicorn
sudo netstat -tlnp | grep 8000
sudo systemctl restart mizrahi-api
sudo journalctl -u mizrahi-api -n 100 --no-pager
```

### Email Not Sending

- Verify `RESEND_API_KEY` is set in `.env`
- Check sender email is verified in Resend dashboard
- Check Resend dashboard for delivery logs

### Apify Actor Failures

```bash
# Verify token
echo $APIFY_API_TOKEN

# Test actor manually
curl -X POST https://api.apify.com/v2/acts/K9WppTziYC3n2vxTu/runs \
  -H "Authorization: Bearer $APIFY_API_TOKEN" \
  -H "Content-Type: application/json"
```

### SSL Certificate Issues

```bash
sudo certbot certificates
sudo certbot renew --dry-run
sudo certbot renew
sudo systemctl restart nginx
```

---

**End of Guide**
