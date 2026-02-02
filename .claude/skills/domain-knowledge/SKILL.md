---
name: domain-knowledge
description: |
  Domain knowledge for Mizrahi Compliance Platform. Use when working on
  validation hooks, fund manager logic, asset types, or regulatory rules.
  Contains Hebrew terminology, manager mappings, and compliance requirements.
allowed-tools: Read, Grep, Glob
---

# Mizrahi Domain Knowledge

Regulatory compliance domain knowledge for Israeli mutual funds.

## Fund Managers

10 fund managers managed by Mizrahi Tefachot trustee:

| Hebrew Name | English | ID | Key |
|-------------|---------|-----|-----|
| מגדל | Migdal | 10040 | migdal |
| איילון | Ayalon | 10054 | ayalon |
| קסם | Kesem | 10047 | kesem |
| סיגמא | Sigma | 10048 | sigma |
| פורסט | Forest | 10082 | forest |
| הראל | Harel | 10031 | harel |
| אנליסט | Analyst | 10019 | analyst |
| מיטב | Meitav | 10083 | meitav |
| איביאי | IBI | 10068 | ibi |
| אלטשולר-שחם | Altshuler Shaham | 10017 | altshuler |

Configuration: `config/managers.yaml`

## Validation Hooks

### Hook #1: Monthly Report Validation (monthly_report)
**Status:** Active
**Schedule:** 5th of month at 09:00 IST
**Purpose:** Validate monthly fund holdings reports

**Checks:**
| ID | Hebrew Name | Description |
|----|-------------|-------------|
| `completeness` | בדיקת שלמות | Cross-reference Magna vs Manager |
| `unusual_assets` | סוגי נכסים חריגים | Flag unusual asset types |
| `new_assets` | נכסים חדשים | New assets since previous month |
| `quantity_changes` | שינויים בכמות | Unusual quantity changes |
| `clause_328` | סעיף 328 | Borrowed quantity validation |
| `required_combinations` | שילובים נדרשים | Asset type combinations (Clause 214) |
| `price_reasonableness` | סבירות מחירים | Price variance < 7.5% |

### Hook #2: Special Transactions (special_transactions)
**Status:** Development
**Schedule:** Manual trigger
**Purpose:** Validate special inter-fund transactions

**Checks:**
| ID | Hebrew Name | Description |
|----|-------------|-------------|
| `duplicates` | עסקאות כפולות | Inter-fund buy/sell pairs |
| `dates` | תאריכים | Transaction date validation |
| `decision_method` | שיטת החלטה | Decision method & דחצ voting |
| `sampling` | דגימה | 5 random samples for review |
| `prices` | מחירים | TASE price verification |
| `problematic_securities` | ניירות בעייתיים | Warning/halt/restricted list |

### Hook #3: Financial Report (financial_report)
**Status:** Specification (Planned Q1 2026)

## Asset Type Classifications

### Unusual Asset Types
Require special attention in reports:
```
16, 21, 22, 23, 24, 52, 53, 57, 58, 99, 101, 112, 201, 207, 209
```

### Required Combinations (Clause 214)
Certain asset types require related types:

| Primary Type | Required Types |
|--------------|----------------|
| 111 | 38, 42, 45, 47, 49, 56 |
| 212 | 326, 327 |
| 213 | 319 |
| 208 | 307 |
| 210 | 310 |

## Transaction Classifications

### Transaction Types
| Code | Type |
|------|------|
| 1, 3, 5 | Buy |
| 2, 4, 6 | Sell |

### Decision Methods
| Method | Required For |
|--------|--------------|
| Type 1 | Transaction types {12, 22} |
| Type 1 or 2 | Transaction types {31, 32, 33, 34, 35, 36} |

### דחצ (External Director) Votes
- Vote 1: Approved
- Vote 2: Approved with conditions
- Check: `has_any_dachatz_vote_1`, `has_any_dachatz_vote_2`

## Regulatory References

### Clause 328
- Borrowed quantity must be consistent with holdings
- Flag discrepancies in borrowed securities
- Compare with previous month data

### Clause 214
- Required asset type combinations
- Enforces regulatory compliance rules
- Configuration in `hooks.yaml`

## External Services

### Apify (Web Scraping)
- **Funds List Actor:** `K9WppTziYC3n2vxTu`
- **Reports Actor:** `5lhI6O39Qbgv9O0gs`
- **Source:** TASE Maya system

### TASE (Tel Aviv Stock Exchange)
- Market price data for price validation
- Warning/halt/restricted security lists

## Configuration Reference

### hooks.yaml Structure
```yaml
hooks:
  monthly_report:
    status: active
    schedule:
      enabled: true
      cron: "0 9 5 * *"
      timezone: Asia/Jerusalem
    parameters:
      unusual_asset_types: [16, 21, ...]
      price_variance_threshold: 7.5
    checks:
      - id: completeness
        name_he: בדיקת שלמות
        enabled: true
```

### managers.yaml Structure
```yaml
managers:
  migdal:
    id: "10040"
    name_he: מגדל
    name_en: Migdal
    enabled: true
```

## Hebrew Terminology

| Hebrew | English | Context |
|--------|---------|---------|
| קרן | Fund | Mutual fund |
| מנהל | Manager | Fund manager |
| נכס | Asset | Fund holding |
| עסקה | Transaction | Trade |
| דחצ | External Director | Board member vote |
| מגנא | Magna | Regulatory system |
| בורסה | Stock Exchange | TASE |
