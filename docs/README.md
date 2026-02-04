# Mizrahi Compliance Platform Documentation

> **BRANCH WARNING**: This is the `legacy/digitalocean-hosting` branch.
> **DO NOT merge this branch into `dev` or `main`**.

Welcome to the documentation for the Mizrahi Compliance Platform (Legacy Hosting).

---

## Quick Start

### Server Deployment

```bash
cd deploy/digitalocean
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export APIFY_API_TOKEN="your_token"
python server.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

---

## Documentation Index

| Document                                         | Description              |
| ------------------------------------------------ | ------------------------ |
| [System Guide](./guides/SYSTEM_GUIDE.md)         | System operations guide  |
| [Batch Processing](./guides/BATCH_PROCESSING.md) | Running batch validation |
| [Cheatsheet](./CHEATSHEET.md)                    | Quick reference commands |

---

## API Endpoints

| Endpoint                         | Method | Description                   |
| -------------------------------- | ------ | ----------------------------- |
| `/`                              | GET    | Health check                  |
| `/api/managers`                  | GET    | List fund managers            |
| `/api/process-report`            | POST   | Hook 2 - Special Transactions |
| `/api/process-monthly-report`    | POST   | Hook 1 - Monthly Report       |
| `/api/process-disclosure-report` | POST   | Hook 5 - K.303 Disclosure     |
| `/api/job/{job_id}`              | GET    | Get job status                |
| `/api/download/{filename}`       | GET    | Download generated report     |

---

## Hooks Overview

| Hook                 | Event ID  | Status     | Description                      |
| -------------------- | --------- | ---------- | -------------------------------- |
| Monthly Report       | 5618      | **Active** | Monthly fund holdings validation |
| Special Transactions | 5615      | **Active** | Coordinated trades validation    |
| K.303 Disclosure     | ISA Magna | **Active** | Disclosure report validation     |

---

## Fund Managers

| Hebrew      | English          | ID    |
| ----------- | ---------------- | ----- |
| מגדל        | Migdal           | 10040 |
| איילון      | Ayalon           | 10054 |
| קסם         | Kesem            | 10047 |
| סיגמא       | Sigma            | 10048 |
| פורסט       | Forest           | 10082 |
| הראל        | Harel            | 10031 |
| אנליסט      | Analyst          | 10019 |
| מיטב        | Meitav           | 10083 |
| איביאי      | IBI              | 10068 |
| אלטשולר-שחם | Altshuler Shaham | 10017 |

---

## Project Structure

```
mizrahi-compliance-platform/
├── frontend/                   # React frontend
│   ├── src/
│   └── package.json
│
├── deploy/
│   └── digitalocean/          # Main deployment code
│       ├── server.py          # Unified FastAPI server
│       ├── scripts/           # Hook processors
│       └── README.md
│
├── config/
│   ├── hooks.yaml            # Hook definitions
│   └── managers.yaml         # Fund manager mappings
│
├── docs/
│   ├── README.md             # This file
│   ├── CHEATSHEET.md         # Quick commands
│   └── guides/               # Operation guides
│
└── .claude/                   # Claude Code configuration
```

---

## Configuration

### hooks.yaml

Defines hook parameters, checks, and schedules:

- Maya TASE Event IDs (5618 for Hook 1, 5615 for Hook 2)
- Validation thresholds
- Check configurations

### managers.yaml

Defines fund managers and Apify settings:

- Manager IDs and Hebrew/English names
- Apify actor IDs
- Trustee name

---

## Environment Variables

| Variable          | Required | Description              |
| ----------------- | -------- | ------------------------ |
| `APIFY_API_TOKEN` | Yes      | Apify API token          |
| `RESEND_API_KEY`  | No       | Resend API key for email |
| `OUTPUT_DIR`      | No       | Output directory         |

---

## External Resources

- **GitHub Repository**: https://github.com/idan82labs/Mizrahi-Platfrom
- **Production API**: https://209.38.226.220.nip.io

---

## Support

For questions or issues:

- Open a GitHub issue
- Contact: elay.g@82labs.io
