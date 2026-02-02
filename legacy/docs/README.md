# Mizrahi Automations - Development Repository

**Last Updated**: 2026-01-15
**Branch**: special-transactions
**Server**: 209.38.226.220

---

## Quick Links

- **[📚 SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** - **START HERE** - Comprehensive system documentation
- **[📦 BATCH_PROCESSING_README.md](BATCH_PROCESSING_README.md)** - Batch processing guide
- **[🚀 Production Server README](/opt/mizrahi/README.md)** - Production API documentation

---

## System Overview

This repository contains **development and automation scripts** for Mizrahi fund validation.

**Production server** runs separately at `/opt/mizrahi/` (see SYSTEM_GUIDE.md)

### Two Main Workflows

1. **Special Transactions Validation**
   - Production: FastAPI server at `https://209.38.226.220.nip.io`
   - Development: Batch scripts in this repo
   - Purpose: Validate coordinated/off-exchange trades

2. **Fund Automation**
   - Script: `fund_automation_complete.py`
   - Trigger: n8n workflow
   - Purpose: Validate fund holdings and asset types

---

## Quick Start

### First Time? Read This First!

📖 **[Open SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** for complete system architecture

### Check Server Status

```bash
# Production API
curl https://209.38.226.220.nip.io/health

# Check running process
ps aux | grep uvicorn
```

### Run Development Scripts

```bash
# Activate virtual environment
source mizrahi-venv/bin/activate

# Test special transactions (one manager)
python test_special_transactions_all_managers.py

# Batch processing (all managers)
export APIFY_TOKEN="<APIFY_API_TOKEN>"
python batch_special_transactions.py --apify-token "$APIFY_TOKEN" --skip-tase-prices

# Fund automation (via n8n)
python fund_automation_complete.py --fund-name "סיגמא"
```

---

## Repository Structure

```
/root/                                    # Development Repository (Git)
├── README.md                            # This file
├── SYSTEM_GUIDE.md                      # 📚 Comprehensive system guide
├── BATCH_PROCESSING_README.md           # Batch processing guide
│
├── mizrahi_special_transactions.py      # Core validation engine
├── batch_special_transactions.py        # Batch processor
├── test_special_transactions_all_managers.py  # Test script
├── send_batch_email.py                  # Email sender (Gmail SMTP)
├── send_test_results.py                 # Test email sender
├── fund_automation_complete.py          # Fund automation (n8n)
│
├── mizrahi_special_transactions_workflow.json  # n8n workflow
├── batch_output/                        # Batch processing results
├── log/                                 # Processing logs
├── output/                              # Individual outputs
├── special_transactions_test/           # Test results
└── Mizrahi-Automations/                 # Backup scripts

/opt/mizrahi/                            # Production Server
├── server.py                            # FastAPI application
├── mizrahi_special_transactions.py      # Production validation engine
├── README.md                            # Production API docs
└── (systemd service: mizrahi-api)
```

---

## Key Information

### Production Server
- **URL**: https://209.38.226.220.nip.io
- **Location**: `/opt/mizrahi/`
- **Service**: `mizrahi-api.service` (systemd)
- **Port**: 8000 (proxied via nginx on 443)

### API Keys
- **Resend**: `<RESEND_API_KEY>`
- **Apify**: `<APIFY_API_TOKEN>`

### Email
- **Production**: Resend API (`notifications@82labs.io`)
- **Development**: Gmail SMTP (requires app password)
- **Recipients**: `idan.t@82labs.io`, `elay.g@82labs.io`

### Infrastructure
- **Domain**: `209.38.226.220.nip.io` (wildcard DNS via nip.io)
- **SSL**: Let's Encrypt
- **Proxy**: Nginx
- **Frontend**: https://mizrahi-smart-tools-portal.vercel.app

---

## Common Tasks

### Update Production Code

```bash
# 1. Make changes in /root/ (development)
cd /root
git add .
git commit -m "Description"

# 2. Copy to production
sudo cp mizrahi_special_transactions.py /opt/mizrahi/
sudo cp server.py /opt/mizrahi/

# 3. Restart production service
sudo systemctl restart mizrahi-api

# 4. Verify
curl https://209.38.226.220.nip.io/health
```

### Run Batch Processing

```bash
cd /root
source mizrahi-venv/bin/activate

# Set token
export APIFY_TOKEN="<APIFY_API_TOKEN>"

# Run for all managers (fast - skips TASE prices)
python batch_special_transactions.py \
  --apify-token "$APIFY_TOKEN" \
  --skip-tase-prices

# Or specific managers
python batch_special_transactions.py \
  --apify-token "$APIFY_TOKEN" \
  --managers "מגדל,סיגמא" \
  --skip-tase-prices
```

### Check Logs

```bash
# Production server logs
sudo journalctl -u mizrahi-api -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log

# Development logs
tail -f /root/log/mizrahi_*.log
```

---

## Fund Managers

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

## Troubleshooting

### Server Not Responding
```bash
sudo systemctl status mizrahi-api
sudo systemctl restart mizrahi-api
sudo systemctl restart nginx
```

### Script Errors
```bash
# Check Python environment
source mizrahi-venv/bin/activate
python --version
pip list | grep -E "fastapi|resend|openpyxl|selenium"
```

### Email Issues
- Production: Check Resend API key
- Development: Use Gmail App Password (not regular password)

### More Help
See **[SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** for detailed troubleshooting

---

## Documentation Index

| File | Purpose |
|------|---------|
| **[SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** | Complete system architecture and reference |
| **[BATCH_PROCESSING_README.md](BATCH_PROCESSING_README.md)** | Batch processing workflows |
| **[/opt/mizrahi/README.md](/opt/mizrahi/README.md)** | Production API documentation |
| **[/opt/mizrahi/LOVABLE.md](/opt/mizrahi/LOVABLE.md)** | Frontend integration guide |
| **[/opt/mizrahi/CLAUDE.md](/opt/mizrahi/CLAUDE.md)** | Claude Code setup notes |

---

## For Claude Code Sessions

When starting a new session:

1. ✅ Read **[SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** first
2. ✅ Check if working on production (`/opt/mizrahi/`) or development (`/root/`)
3. ✅ Verify server status: `curl https://209.38.226.220.nip.io/health`
4. ✅ Understand the workflow: Special Transactions vs Fund Automation
5. ✅ Check git status: `git status`

---

**Last updated**: 2026-01-15 by Claude Code
