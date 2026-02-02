# Mizrahi System Architecture Guide

**Last Updated**: 2026-01-15
**Purpose**: Comprehensive guide for understanding the Mizrahi fund validation and automation system

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Production Server](#production-server)
4. [Development Repository](#development-repository)
5. [Special Transactions Workflow](#special-transactions-workflow)
6. [Fund Automation Workflow](#fund-automation-workflow)
7. [Email System](#email-system)
8. [Infrastructure](#infrastructure)
9. [Common Operations](#common-operations)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

The Mizrahi system consists of two main automation workflows:

1. **Special Transactions Validation** - Validates special transactions reports from fund managers
2. **Fund Automation** - Validates fund holdings and asset types

Both workflows:
- Fetch data from TASE (Tel Aviv Stock Exchange) via Apify actors
- Process and validate according to regulatory rules
- Generate Excel reports
- Send results via email

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend: mizrahi-smart-tools-portal.vercel.app            │
│  (React/Next.js application)                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS
                  │
┌─────────────────▼───────────────────────────────────────────┐
│  209.38.226.220.nip.io (SSL via Let's Encrypt)              │
│  ├── Nginx (ports 80/443)                                   │
│  └── Reverse proxy to localhost:8000                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│  Production Server: /opt/mizrahi/                           │
│  ├── server.py (FastAPI + Uvicorn on port 8000)            │
│  ├── mizrahi_special_transactions.py (Validation engine)    │
│  └── Managed by systemd (mizrahi-api.service)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Development/Automation: /root/                             │
│  ├── Git repository (branch: special-transactions)          │
│  ├── Batch processing scripts                               │
│  └── n8n integration (fund_automation_complete.py)         │
└─────────────────────────────────────────────────────────────┘

External Services:
  ├── Apify API (Web scraping actors)
  ├── Resend API (Email delivery)
  └── TASE Maya (Data source)
```

---

## Production Server

### Location
**Path**: `/opt/mizrahi/`

### Running Process
```bash
# Check if server is running
ps aux | grep uvicorn
# Output: uvicorn server:app --host 0.0.0.0 --port 8000 (PID: 440661)

# Check systemd service
systemctl status mizrahi-api.service
```

### Key Files

| File | Purpose |
|------|---------|
| `server.py` | FastAPI application (main API server) |
| `mizrahi_special_transactions.py` | Core validation engine |
| `test_mode.py` | Test mode for validations |
| `Mutual_Funds_List.xlsx` | Static fallback funds list |
| `Special_Transactions_Specifications.xlsx` | Validation rules spec |
| `mizrahi-api.service` | Systemd service configuration |
| `nginx.conf` | Nginx reverse proxy config |
| `requirements.txt` | Python dependencies |

### Key Dependencies
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
httpx==0.26.0
resend==0.8.0
openpyxl==3.1.2
selenium==4.17.2
```

### Environment Variables
```bash
RESEND_API_KEY=<RESEND_API_KEY>
APIFY_API_TOKEN=<APIFY_API_TOKEN>
FROM_EMAIL=notifications@82labs.io
```

### API Endpoints

#### GET `/`
Health check and service info
```json
{
  "status": "ok",
  "service": "Mizrahi Special Transactions API",
  "version": "3.0.0"
}
```

#### GET `/api/managers`
List available fund managers
```json
{
  "managers": [
    {"name": "מגדל", "item_id": "10040"},
    {"name": "איילון", "item_id": "10054"},
    ...
  ]
}
```

#### POST `/api/process-report`
Process special transactions report (auto-downloads from TASE)

**Form Data**:
- `manager_name`: Fund manager name (Hebrew)
- `email`: Recipient email(s), semicolon-separated
- `price_threshold`: Price variance threshold % (default: 5.0)
- `skip_tase_prices`: Skip TASE price scraping (default: true)

**Response**:
```json
{
  "job_id": "uuid",
  "status": "queued",
  "message": "Processing started"
}
```

#### GET `/api/job/{job_id}`
Check job status

**Statuses**: `queued` → `downloading` → `processing` → `sending_email` → `completed` | `failed`

#### GET `/api/download/{filename}`
Download generated report file

---

## Development Repository

### Location
**Path**: `/root/`
**Git Branch**: `special-transactions`
**Git User**: `idan.t@82labs.io`

### Key Files

| File | Purpose |
|------|---------|
| `mizrahi_special_transactions.py` | Core validation engine (development version) |
| `batch_special_transactions.py` | Batch processing for multiple managers |
| `test_special_transactions_all_managers.py` | Test all managers |
| `send_batch_email.py` | Gmail SMTP email sender |
| `fund_automation_complete.py` | Fund automation (triggered via n8n) |
| `mizrahi_special_transactions_workflow.json` | n8n workflow configuration |

### Directories

| Directory | Purpose |
|-----------|---------|
| `batch_output/` | Batch processing results |
| `log/` | Processing logs |
| `output/` | Individual report outputs |
| `special_transactions_test/` | Test results |
| `Mizrahi-Automations/` | Backup/copy of automation scripts |

---

## Special Transactions Workflow

### Purpose
Validate special transactions (coordinated/off-exchange trades) reported by fund managers.

### Process Flow

```
1. User selects manager from frontend
   ↓
2. Frontend calls POST /api/process-report
   ↓
3. Server downloads main funds list from Maya (via Apify)
   ↓
4. Server downloads special transactions report (via Apify)
   ↓
5. Server processes report with validation engine
   ↓
6. Server generates Excel report with all checks
   ↓
7. Server sends main report email (via Resend)
   ↓
8. Server sends samples forward email (via Resend)
   ↓
9. User receives emails with attachments
```

### Validation Checks

| Check # | Name | Description |
|---------|------|-------------|
| CHK_1 | Duplicate Transactions | Identifies transactions between Mizrahi funds (buy/sell pairs) |
| CHK_2 | Fund Scope | Filters to Mizrahi-trusteed funds only |
| CHK_3 | Date Validation | Ensures transaction dates fall within report month |
| CHK_4 | Decision Method Rules | Validates decision method codes (1 or 2) |
| CHK_5 | Sampling | Selects random samples for manual verification |
| CHK_6 | TASE Price Validation | Cross-checks prices with TASE market data (optional, slow) |
| CHK_7 | Problematic Securities | Flags securities on warning/halt/restricted lists |

### Output Format

Excel workbook with sheets:
- **Summary**: Overview statistics
- **Check Statuses**: Pass/fail for each validation
- **Duplicates**: Inter-fund transactions
- **Date Exceptions**: Transactions outside report month
- **Decision Exceptions**: Invalid decision methods
- **Samples**: Random samples for verification
- **Price Checks**: Price variance analysis (if enabled)
- **Problematic Securities**: Flagged securities
- **Out of Scope**: Non-Mizrahi funds

### Apify Actors Used

| Actor ID | Purpose |
|----------|---------|
| `5lhI6O39Qbgv9O0gs` | Download special transactions reports from Maya |
| `K9WppTziYC3n2vxTu` | Download main funds list from Maya |

---

## Fund Automation Workflow

### Purpose
Validate fund holdings and asset types for regulatory compliance.

### Location
**Script**: `/root/fund_automation_complete.py`
**Trigger**: n8n workflow automation

### Process Flow

```
1. n8n scheduler triggers at specified time
   ↓
2. Calls fund_automation_complete.py with --fund-name
   ↓
3. Script fetches master funds list (via Apify)
   ↓
4. Script fetches current + previous month reports (via Apify)
   ↓
5. Script processes with 7 validation checks
   ↓
6. Script generates Excel report
   ↓
7. n8n sends email with report (configured in workflow)
```

### Validation Checks

| Check # | Name | Description | Threshold |
|---------|------|-------------|-----------|
| 1 | Fund Completeness | Cross-reference Magna vs Manager reports | - |
| 2 | Unusual Asset Types | Flag non-standard asset types with value > 0 | Types: 16,21,22,23,24,52,53,57,58,99,101,112,201,207,209 |
| 3 | New Assets | Assets added since previous month | - |
| 4 | Asset Quantity Changes | Unusual asset quantity changes month-over-month | - |
| 5 | Clause 328 | Borrowed quantity consistency check | - |
| 6 | Required Combinations | Asset type pairs that must appear together | Various rules |
| 7 | Price Reasonableness | Price ratio validation | 7.5% variance |

### Required Asset Combinations

```python
REQUIRED_COMBINATIONS = {
    111: [38, 42, 45, 47, 49, 56],  # If any of these ≥100k, need 111
    212: [326, 327],
    213: [319],
    208: [307],
    210: [310],
}
```

### Fund Manager Codes

```python
FUND_MANAGER_CODES = {
    "מגדל": "10040",
    "איילון": "10054",
    "קסם": "10047",
    "סיגמא": "10048",
    "פורסט": "10082",
    "הראל": "10031",
    "אנליסט": "10019",
    "מיטב": "10083",
    "איביאי": "10068",
    "אלטשולר-שחם": "10017",
}
```

### n8n Integration

**Workflow File**: `mizrahi_special_transactions_workflow.json`

The n8n workflow:
1. Runs on schedule (configured in n8n)
2. Executes `fund_automation_complete.py` with manager name
3. Captures Excel output
4. Sends email with attachment
5. Logs results

---

## Email System

### Production (Resend API)

**Used by**: Production server (`/opt/mizrahi/server.py`)

```python
# Configuration
RESEND_API_KEY = "<RESEND_API_KEY>"
FROM_EMAIL = "notifications@82labs.io"

# Send function
resend.Emails.send({
    "from": FROM_EMAIL,
    "to": ["recipient@example.com"],
    "subject": "Subject",
    "html": html_body,
    "attachments": [{"filename": "report.xlsx", "content": base64_content}]
})
```

### Email Types

#### 1. Main Report Email
- **To**: User-specified recipients
- **Subject**: `דוח עסקאות מיוחדות - {manager_name}`
- **Attachments**: Excel report
- **Template**: HTML with RTL Hebrew formatting

#### 2. Samples Forward Email
- **To**: User-specified recipients
- **Subject**: `{manager_name} - דגימה לעסקאות מיוחדות {YYYY-MM}`
- **Content**: Table of sampled transactions for fund manager inquiry
- **Purpose**: Forward to fund manager for verification

### Development (Gmail SMTP)

**Used by**: Batch scripts (`send_batch_email.py`, `send_test_results.py`)

```python
# Configuration
smtp.gmail.com:465 (SSL)

# Requires:
# - Gmail App Password (not regular password)
# - 2FA enabled on Google account
```

---

## Infrastructure

### nip.io Domain

**Domain**: `209.38.226.220.nip.io`

nip.io is a wildcard DNS service that automatically resolves to the IP address in the subdomain.

- `209.38.226.220.nip.io` → `209.38.226.220`
- Allows HTTPS with Let's Encrypt without owning a domain
- Perfect for development/testing environments

### Nginx Configuration

**File**: `/etc/nginx/sites-enabled/default` (or similar)

```nginx
server {
    server_name 209.38.226.220.nip.io 209.38.226.220;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
        proxy_read_timeout 300s;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/209.38.226.220.nip.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/209.38.226.220.nip.io/privkey.pem;
}
```

### SSL Certificate

**Provider**: Let's Encrypt
**Domain**: `209.38.226.220.nip.io`
**Renewal**: Automatic via certbot

```bash
# Check certificate
sudo certbot certificates

# Renew manually (if needed)
sudo certbot renew
```

### Systemd Service

**File**: `/opt/mizrahi/mizrahi-api.service`

```bash
# Start/stop/restart
sudo systemctl start mizrahi-api
sudo systemctl stop mizrahi-api
sudo systemctl restart mizrahi-api

# View logs
sudo journalctl -u mizrahi-api -f
```

### Server IP Addresses

```
Public IP:  209.38.226.220
Private IP: 10.19.0.5, 10.114.0.2
```

---

## Common Operations

### Check Production Server Status

```bash
# Check if API is running
curl https://209.38.226.220.nip.io/health

# Check process
ps aux | grep uvicorn

# Check logs
sudo journalctl -u mizrahi-api -n 100

# Check nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/access.log
```

### Restart Production Server

```bash
sudo systemctl restart mizrahi-api
sudo systemctl restart nginx
```

### Run Development Scripts

```bash
# Activate virtual environment
cd /root
source mizrahi-venv/bin/activate

# Test single manager
python test_special_transactions_all_managers.py

# Run batch processing
python batch_special_transactions.py

# Run fund automation
python fund_automation_complete.py --fund-name "סיגמא"
```

### Update Production Code

```bash
# From development to production
cd /root
git pull  # Get latest changes

# Copy to production
sudo cp mizrahi_special_transactions.py /opt/mizrahi/
sudo cp server.py /opt/mizrahi/

# Restart service
sudo systemctl restart mizrahi-api
```

### Check API Keys

```bash
# View environment variables (production)
sudo systemctl cat mizrahi-api | grep Environment

# Or check directly in code
grep -r "RESEND_API_KEY\|APIFY" /opt/mizrahi/server.py
```

### Test Email Sending

```bash
# Via Resend (production)
curl -X POST https://209.38.226.220.nip.io/api/process-report \
  -F "manager_name=מגדל" \
  -F "email=test@example.com"

# Via Gmail SMTP (development)
python send_batch_email.py \
  --batch-dir ./batch_output/20260114_120000 \
  --gmail-user your.email@gmail.com \
  --gmail-app-password YOUR_APP_PASSWORD
```

---

## Troubleshooting

### Production Server Not Responding

```bash
# Check if process is running
ps aux | grep uvicorn

# Check port binding
sudo netstat -tlnp | grep 8000

# Restart service
sudo systemctl restart mizrahi-api

# Check logs
sudo journalctl -u mizrahi-api -n 100 --no-pager
```

### SSL Certificate Issues

```bash
# Check certificate validity
sudo certbot certificates

# Renew if expired
sudo certbot renew --dry-run
sudo certbot renew
sudo systemctl restart nginx
```

### Email Not Sending

**Resend API**:
- Check API key is valid
- Check "from" email is authorized in Resend dashboard
- Check rate limits

**Gmail SMTP**:
- Use App Password, not regular password
- Enable 2FA on Google account
- Check less secure apps setting

### Apify Actor Failures

```bash
# Check Apify token
echo $APIFY_API_TOKEN

# Test actor manually
curl -X POST https://api.apify.com/v2/acts/5lhI6O39Qbgv9O0gs/runs \
  -H "Authorization: Bearer $APIFY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://maya.tase.co.il/..."}'
```

### Frontend Can't Connect

```bash
# Check CORS settings in server.py
grep -A 10 "CORS" /opt/mizrahi/server.py

# Check nginx proxy
sudo nginx -t
sudo tail -f /var/log/nginx/error.log

# Check if API responds
curl -X GET https://209.38.226.220.nip.io/health
```

### File Permission Issues

```bash
# Fix ownership (if needed)
sudo chown -R root:root /opt/mizrahi/
sudo chmod 644 /opt/mizrahi/*.py
sudo chmod 755 /opt/mizrahi/*.sh

# Check output directory
ls -la /tmp/mizrahi-outputs/
```

---

## Quick Reference

### Key Ports
- **80**: HTTP (redirects to HTTPS)
- **443**: HTTPS (nginx)
- **8000**: Uvicorn/FastAPI (internal)

### Key URLs
- **Production API**: https://209.38.226.220.nip.io
- **Frontend**: https://mizrahi-smart-tools-portal.vercel.app
- **TASE Maya**: https://maya.tase.co.il
- **Apify API**: https://api.apify.com/v2

### Key People/Contacts
- **Email Recipients**: `idan.t@82labs.io`, `elay.g@82labs.io`
- **Git User**: `idan.t@82labs.io`

### Important Notes

1. **Two Separate Codebases**:
   - Production: `/opt/mizrahi/` (deployed, running)
   - Development: `/root/` (git repo, testing)

2. **Email Systems**:
   - Production uses Resend API (modern, reliable)
   - Development uses Gmail SMTP (legacy, for batch scripts)

3. **nip.io Magic**:
   - `209.38.226.220.nip.io` automatically resolves to `209.38.226.220`
   - Allows HTTPS without owning a domain
   - Perfect for development servers

4. **Apify Actors**:
   - Special Transactions: `5lhI6O39Qbgv9O0gs`
   - Main Funds List: `K9WppTziYC3n2vxTu`

5. **Hebrew Files**:
   - Some CSV files have shifted encoding (0x10 offset)
   - `fix_shifted_encoding()` function handles this

---

## Next Steps for New Sessions

When starting a new Claude Code session:

1. **Read this guide first** - `/root/SYSTEM_GUIDE.md`
2. **Check server status** - `curl https://209.38.226.220.nip.io/health`
3. **Verify location** - Development work in `/root/`, production in `/opt/mizrahi/`
4. **Check git status** - `cd /root && git status`
5. **Understand the task** - Is it special transactions or fund automation?

---

**End of Guide**
