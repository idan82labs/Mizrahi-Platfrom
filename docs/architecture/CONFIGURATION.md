# Configuration Format

This document describes the YAML configuration files for hooks, managers, and
environments.

**Related Documents:**

- [Hook System](./HOOK_SYSTEM.md) - Hook plugin architecture
- [System Design](./SYSTEM_DESIGN.md) - Overall structure

---

## Table of Contents

1. [hooks.yaml](#hooksyaml)
2. [managers.yaml](#managersyaml)
3. [Environment Configuration](#environment-configuration)

---

## hooks.yaml

Hook definitions, schedules, parameters, and checks.

```yaml
# config/hooks.yaml
# Hook definitions and schedules

version: '1.0'

defaults:
  timezone: 'Asia/Jerusalem'
  email:
    from: 'notifications@82labs.io'
    provider: 'resend'

hooks:
  # ============================================
  # Hook #1: Monthly Report Validation
  # ============================================
  monthly_report:
    id: 'monthly_report'
    name: 'Monthly Report Validation'
    name_he: 'בקרה אוטומטית על דוח חודשי'
    description: 'Validates monthly fund holdings reports against Magna list'
    status: 'active'

    schedule:
      enabled: true
      cron: '0 9 5 * *' # 5th of every month at 09:00
      timezone: 'Asia/Jerusalem'

    parameters:
      # Price check threshold (percentage)
      price_variance_threshold: 7.5

      # Asset types flagged as unusual
      unusual_asset_types:
        - 16
        - 21
        - 22
        - 23
        - 24
        - 52
        - 53
        - 57
        - 58
        - 99
        - 101
        - 112
        - 201
        - 207
        - 209

      # Required asset type combinations (Clause 214)
      # Key: required type, Value: triggering types
      required_combinations:
        111: [38, 42, 45, 47, 49, 56] # If any >= 100,000 ILS
        212: [326, 327]
        213: [319]
        208: [307]
        210: [310]

      # Minimum value to trigger combination check
      combination_threshold_ils: 100000

      # Apify actor IDs
      funds_list_actor: 'K9WppTziYC3n2vxTu'
      reports_actor: '5lhI6O39Qbgv9O0gs'

    checks:
      - id: 'completeness'
        name: 'Completeness Check'
        name_he: 'בדיקת שלמות'
        description: 'Cross-reference Magna vs Manager reports'
        enabled: true

      - id: 'unusual_assets'
        name: 'Unusual Asset Types'
        name_he: 'סוגי נכסים חריגים'
        description: 'Flag unusual asset types with value > 0'
        enabled: true

      - id: 'new_assets'
        name: 'New Assets'
        name_he: 'נכסים חדשים'
        description: 'New assets added since previous month'
        enabled: true

      - id: 'quantity_changes'
        name: 'Quantity Changes'
        name_he: 'שינויים בכמות'
        description: 'Unusual quantity changes month-over-month'
        enabled: true

      - id: 'clause_328'
        name: 'Clause 328'
        name_he: 'סעיף 328'
        description: 'Borrowed quantity consistency check'
        enabled: true

      - id: 'required_combinations'
        name: 'Required Combinations'
        name_he: 'שילובים נדרשים'
        description: 'Required asset type combinations (Clause 214)'
        enabled: true

      - id: 'price_reasonableness'
        name: 'Price Reasonableness'
        name_he: 'סבירות מחירים'
        description: 'Price ratio validation'
        enabled: true

    email:
      enabled: true
      template: 'monthly_report'
      recipients_from_input: true
      cc:
        - 'elay.g@82labs.io'

    output:
      format: 'xlsx'
      include_review_columns: true # האם תקין?, שם הבודק

  # ============================================
  # Hook #2: Special Transactions Validation
  # ============================================
  special_transactions:
    id: 'special_transactions'
    name: 'Special Transactions Validation'
    name_he: 'בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה'
    description: 'Validates coordinated/off-exchange trades'
    status: 'development'

    schedule:
      enabled: false # Manual trigger only for now
      cron: '0 10 5 * *' # Planned: 5th at 10:00
      timezone: 'Asia/Jerusalem'

    parameters:
      # Price variance threshold (percentage)
      price_variance_threshold: 5.0

      # Number of random samples for manual verification
      sample_size: 5

      # Skip TASE price scraping (slow, requires Selenium)
      skip_tase_prices: true

      # Transaction types requiring decision method 1
      decision_types_requiring_1:
        - 12
        - 22

      # Transaction types requiring decision method 1 or 2
      decision_types_requiring_1_or_2:
        - 31
        - 32
        - 33
        - 34
        - 35
        - 36

      # Apify configuration
      funds_list_actor: 'K9WppTziYC3n2vxTu'
      reports_actor: '5lhI6O39Qbgv9O0gs'
      event_id: 5618

    checks:
      - id: 'chk1_duplicates'
        name: 'Duplicates'
        name_he: 'עסקאות כפולות'
        description: 'Inter-fund transactions (buy/sell pairs)'
        enabled: true

      - id: 'chk3_dates'
        name: 'Date Validation'
        name_he: 'חריגות תאריך'
        description: 'Transaction dates within report month'
        enabled: true

      - id: 'chk4_decision'
        name: 'Decision Method'
        name_he: 'שיטת ההחלטה'
        description: 'Decision method and דחצ voting rules'
        enabled: true
        sub_checks:
          - id: 'chk4a_method_required'
            name_he: 'שיטת החלטה נדרשת'
          - id: 'chk4g_dachatz_vote_required'
            name_he: 'הצבעת דח״צ נדרשת'
          - id: 'chk4d_dachatz_vote_2_flag'
            name_he: 'דח״צ הצביע 2'

      - id: 'chk5_sampling'
        name: 'Sampling'
        name_he: 'דגימות'
        description: 'Random samples for manual verification'
        enabled: true

      - id: 'chk6_prices'
        name: 'TASE Prices'
        name_he: 'בדיקות מחיר'
        description: 'Cross-check with TASE market data'
        enabled: true
        sub_checks:
          - id: 'chk6a_tase_variance'
            name_he: 'סטיית מחיר מהבורסה'
          - id: 'chk6g_internal_discrepancy'
            name_he: 'פער מחיר פנימי'

      - id: 'chk7_problematic'
        name: 'Problematic Securities'
        name_he: 'ניירות בעייתיים'
        description: 'Securities on warning/halt/restricted lists'
        enabled: true

    email:
      enabled: true
      template: 'special_transactions'
      recipients_from_input: true
      include_samples: true # Include transaction samples in email body
      cc:
        - 'elay.g@82labs.io'

    output:
      format: 'xlsx'
      sheets:
        - 'סיכום'
        - 'סטטוס בדיקות'
        - 'עסקאות כפולות'
        - 'חריגות תאריך'
        - 'חריגות החלטה'
        - 'דגימות'
        - 'בדיקות מחיר'
        - 'ניירות בעייתיים'
        - 'מחוץ לטווח'

  # ============================================
  # Hook #3: Financial Report Validation (Future)
  # ============================================
  financial_report:
    id: 'financial_report'
    name: 'Financial Report Validation'
    name_he: 'בדיקת דוח כספי אוטומטית'
    description: 'Automated financial report validation'
    status: 'specification'
    planned_release: 'Q1 2026'

    schedule:
      enabled: false

    parameters: {}
    checks: []

    email:
      enabled: false
```

---

## managers.yaml

Fund manager configuration.

```yaml
# config/managers.yaml
# Fund manager configuration

version: '1.0'

managers:
  migdal:
    id: '10040'
    name_he: 'מגדל'
    name_en: 'Migdal'
    enabled: true
    contact_email: ''

  ayalon:
    id: '10054'
    name_he: 'איילון'
    name_en: 'Ayalon'
    enabled: true
    contact_email: ''

  kesem:
    id: '10047'
    name_he: 'קסם'
    name_en: 'Kesem'
    enabled: true
    contact_email: ''

  sigma:
    id: '10048'
    name_he: 'סיגמא'
    name_en: 'Sigma'
    enabled: true
    contact_email: ''

  forest:
    id: '10082'
    name_he: 'פורסט'
    name_en: 'Forest'
    enabled: true
    contact_email: ''

  harel:
    id: '10031'
    name_he: 'הראל'
    name_en: 'Harel'
    enabled: true
    contact_email: ''

  analyst:
    id: '10019'
    name_he: 'אנליסט'
    name_en: 'Analyst'
    enabled: true
    contact_email: ''

  meitav:
    id: '10083'
    name_he: 'מיטב'
    name_en: 'Meitav'
    enabled: true
    contact_email: ''

  ibi:
    id: '10068'
    name_he: 'איביאי'
    name_en: 'IBI'
    enabled: true
    contact_email: ''

  altshuler:
    id: '10017'
    name_he: 'אלטשולר-שחם'
    name_en: 'Altshuler Shaham'
    enabled: true
    contact_email: ''

# Lookup helpers (generated at load time)
# by_id: {"10040": "migdal", ...}
# by_name_he: {"מגדל": "migdal", ...}
```

---

## Environment Configuration

### Production

```yaml
# config/environments/production.yaml
# Production environment configuration

environment: 'production'

server:
  host: '0.0.0.0'
  port: 8000
  workers: 4
  reload: false

database:
  url: '${DATABASE_URL}'
  pool_size: 10
  max_overflow: 20

redis:
  url: '${REDIS_URL}'
  enabled: true

email:
  provider: 'resend'
  api_key: '${RESEND_API_KEY}'
  from_address: 'notifications@82labs.io'
  from_name: 'Mizrahi Compliance'

apify:
  token: '${APIFY_API_TOKEN}'
  timeout_seconds: 300
  max_retries: 3

logging:
  level: 'INFO'
  format: 'json'

monitoring:
  sentry_dsn: '${SENTRY_DSN}'
  enabled: true

cors:
  allowed_origins:
    - 'https://mizrahi-compliance.82labs.io'
    - 'https://mizrahi-smart-tools-portal.vercel.app'
```

### Development

```yaml
# config/environments/development.yaml
# Development environment configuration

environment: 'development'

server:
  host: '127.0.0.1'
  port: 8000
  workers: 1
  reload: true

database:
  url: 'sqlite:///./dev.db'
  echo: true

redis:
  enabled: false

email:
  provider: 'console' # Print to console instead of sending

apify:
  token: '${APIFY_API_TOKEN}'
  timeout_seconds: 60
  mock_enabled: true # Use cached test data when available

logging:
  level: 'DEBUG'
  format: 'text'

monitoring:
  enabled: false

cors:
  allowed_origins:
    - 'http://localhost:5173'
    - 'http://localhost:3000'
```

---

**Next:** [API Design](./API_DESIGN.md)
