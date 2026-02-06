# Mizrahi System - Quick Cheat Sheet

## Deployment Location

```
/opt/mizrahi/             Production (systemd service)
deploy/digitalocean/      Development (git repo)
```

## URLs

```
Production API:  https://209.38.226.220.nip.io
Frontend:        https://mizrahi-smart-tools-portal.vercel.app
```

## Environment Variables

Stored in `deploy/digitalocean/.env` (loaded via python-dotenv):

```bash
APIFY_API_TOKEN=<your_token>    # Required
RESEND_API_KEY=<your_key>       # Required
FROM_EMAIL=noreply@notifications.82labs.io
TASE_API_KEY=<your_key>         # Optional (Hook 4)
```

## Quick Commands

### Check Server Status
```bash
curl https://209.38.226.220.nip.io/health
sudo systemctl status mizrahi-api
```

### Restart Production
```bash
sudo systemctl restart mizrahi-api
sudo systemctl restart nginx
```

### Run Individual Hooks
```bash
cd deploy/digitalocean
./run_hook1.sh --email "your@email.com"
./run_hook2.sh --email "your@email.com"
./run_hook5.sh --email "your@email.com"
```

### Run All Hooks for All Managers
```bash
./run_all_managers.sh --email "your@email.com"
```

### Test Hooks Offline (No Apify Needed)
```bash
./test_offline_hook2.sh סיגמא
./test_offline_hook5.sh מגדל 2025-11
```

## API Endpoints

```
GET  /                              Health check
GET  /api/managers                  List fund managers
POST /api/process-report            Hook 2 - Special Transactions
POST /api/process-monthly-report    Hook 1 - Monthly Report
POST /api/process-disclosure-report Hook 5 - K.303 Disclosure
GET  /api/job/{id}                  Check job status
GET  /api/download/{file}           Download report
```

## Fund Managers (8)

```
מגדל        10040  |  אנליסט      10019
קסם         10047  |  מיטב        10083
סיגמא       10048  |  איביאי      10068
הראל        10031  |  אלטשולר-שחם  10017
```

## Maya Event IDs

```
Hook 1 (Monthly Report):       5618
Hook 2 (Special Transactions): 5615
```

## Email

```
Provider:    Resend API
From:        noreply@notifications.82labs.io
Recipients:  idan.t@82labs.io, elay.g@82labs.io
```

## Infrastructure

```
Server IP:    209.38.226.220
nip.io:       209.38.226.220.nip.io
Nginx:        443 -> localhost:8000
Uvicorn:      localhost:8000
SSL:          Let's Encrypt (certbot)
```

## Troubleshooting

```bash
# Server down?
sudo systemctl restart mizrahi-api

# Check port 8000
sudo netstat -tlnp | grep 8000

# SSL cert expired?
sudo certbot renew && sudo systemctl restart nginx

# View logs
sudo journalctl -u mizrahi-api -f
```

## Full Documentation

See `docs/guides/SYSTEM_GUIDE.md` for complete reference.
