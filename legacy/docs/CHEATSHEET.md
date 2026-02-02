# Mizrahi System - Quick Cheat Sheet

## 🚨 Two Separate Codebases

| Location | Purpose | Running |
|----------|---------|---------|
| `/opt/mizrahi/` | **Production** (deployed API) | ✅ systemd service |
| `/root/` | **Development** (git repo) | Manual scripts |

## 🌐 URLs

```
Production API:  https://209.38.226.220.nip.io
Frontend:        https://mizrahi-smart-tools-portal.vercel.app
TASE Maya:       https://maya.tase.co.il
```

## 🔑 Credentials

```bash
APIFY_API_TOKEN=<APIFY_API_TOKEN>
RESEND_API_KEY=<RESEND_API_KEY>
FROM_EMAIL=notifications@82labs.io
```

## 🎯 Quick Commands

### Check Server Status
```bash
curl https://209.38.226.220.nip.io/health
ps aux | grep uvicorn
sudo systemctl status mizrahi-api
```

### Restart Production
```bash
sudo systemctl restart mizrahi-api
sudo systemctl restart nginx
```

### View Logs
```bash
sudo journalctl -u mizrahi-api -f
sudo tail -f /var/log/nginx/access.log
```

### Run Development Script
```bash
cd /root
source mizrahi-venv/bin/activate
export APIFY_TOKEN="<APIFY_API_TOKEN>"
python batch_special_transactions.py --apify-token "$APIFY_TOKEN" --skip-tase-prices
```

### Update Production Code
```bash
# Edit in /root/, then:
sudo cp /root/server.py /opt/mizrahi/
sudo systemctl restart mizrahi-api
```

## 📋 API Endpoints

```
GET  /health              - Health check
GET  /api/managers        - List fund managers
POST /api/process-report  - Start processing (manager_name, email)
GET  /api/job/{id}        - Check job status
GET  /api/download/{file} - Download report
```

## 👥 Fund Managers

```
מגדל    10040  |  פורסט       10082
איילון   10054  |  הראל        10031
קסם     10047  |  אנליסט      10019
סיגמא    10048  |  מיטב        10083
איביאי   10068  |  אלטשולר-שחם  10017
```

## 🔧 Infrastructure

```
Server IP:    209.38.226.220
nip.io:       209.38.226.220.nip.io → 209.38.226.220
Nginx:        443 → localhost:8000
Uvicorn:      localhost:8000
SSL:          Let's Encrypt
Git User:     idan.t@82labs.io
```

## 📧 Email

```
Production:   Resend API (notifications@82labs.io)
Development:  Gmail SMTP (requires app password)
Recipients:   idan.t@82labs.io, elay.g@82labs.io
```

## 🔄 Workflows

**Special Transactions** (Production)
```
Frontend → API → Apify → Process → Email (Resend)
```

**Fund Automation** (n8n)
```
n8n Scheduler → fund_automation_complete.py → Email (n8n)
```

## 🐛 Quick Troubleshooting

```bash
# Server down?
sudo systemctl restart mizrahi-api

# Check if port 8000 is bound
sudo netstat -tlnp | grep 8000

# Test API manually
curl -X POST https://209.38.226.220.nip.io/api/process-report \
  -F "manager_name=מגדל" \
  -F "email=test@example.com"

# SSL cert expired?
sudo certbot renew
sudo systemctl restart nginx
```

## 📚 Full Documentation

See **SYSTEM_GUIDE.md** for complete reference
