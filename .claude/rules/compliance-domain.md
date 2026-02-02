---
paths:
  - "packages/hooks/**/*.py"
  - "config/hooks.yaml"
---

# Compliance Domain Rules

Domain-specific rules for the Mizrahi Compliance Platform validation logic.

## Fund Managers

10 fund managers configured in `config/managers.yaml`:

| Hebrew Name | ID | Key |
|-------------|-----|-----|
| מגדל | 10040 | migdal |
| איילון | 10054 | ayalon |
| קסם | 10047 | kesem |
| סיגמא | 10048 | sigma |
| פורסט | 10082 | forest |
| הראל | 10031 | harel |
| אנליסט | 10019 | analyst |
| מיטב | 10083 | meitav |
| איביאי | 10068 | ibi |
| אלטשולר-שחם | 10017 | altshuler |

## Validation Hooks

### Hook #1: Monthly Report (monthly_report)
Validates monthly fund holdings reports.

**Checks:**
1. `completeness` — Cross-reference Magna vs Manager reports
2. `unusual_assets` — Flag unusual asset types
3. `new_assets` — Detect new assets since previous month
4. `quantity_changes` — Identify unusual quantity changes
5. `clause_328` — Borrowed quantity validation
6. `required_combinations` — Asset type combination rules (Clause 214)
7. `price_reasonableness` — Price variance < 7.5%

### Hook #2: Special Transactions (special_transactions)
Validates special transactions between funds.

**Checks:**
1. `duplicates` — Inter-fund buy/sell pairs
2. `dates` — Transaction date validation
3. `decision_method` — Decision method & דחצ voting
4. `sampling` — 5 random samples for manual review
5. `prices` — TASE market price verification (< 5% variance)
6. `problematic_securities` — Warning/halt/restricted list

### Hook #3: Financial Report (financial_report)
Planned for Q1 2026 — not yet implemented.

## Regulatory References

### Clause 328
- Borrowed quantity must be consistent with holdings
- Flag discrepancies in borrowed securities

### Clause 214 (Required Combinations)
- Certain asset types require related asset types
- Configuration in `hooks.yaml` under `required_combinations`

```yaml
required_combinations:
  111: [38, 42, 45, 47, 49, 56]
  212: [326, 327]
  213: [319]
  208: [307]
  210: [310]
```

## Asset Type Classifications

### Unusual Asset Types
Types that require special attention:
```
16, 21, 22, 23, 24, 52, 53, 57, 58, 99, 101, 112, 201, 207, 209
```

### Transaction Types
- Buy: 1, 3, 5
- Sell: 2, 4, 6

### Decision Methods
- Type 1: Required for transaction types {12, 22}
- Type 1 or 2: Required for types {31, 32, 33, 34, 35, 36}

## Configuration

All validation parameters externalized to `config/hooks.yaml`:

```yaml
hooks:
  monthly_report:
    parameters:
      unusual_asset_types: [16, 21, 22, ...]
      price_variance_threshold: 7.5
      required_combinations:
        111: [38, 42, 45, 47, 49, 56]
```

Access in code via `self.get_parameter("key", default)`.

## Output Format

### Check Result
```python
CheckResult(
    check_id="completeness",
    check_name_he="בדיקת שלמות",
    status="fail",  # pass | fail | warning | skipped
    message="נמצאו 3 קרנות חסרות",
    findings_count=3,
    findings=[
        {"מספר קרן": "12345", "שם קרן": "...", "סטטוס": "חסר"}
    ]
)
```

### Excel Report
- Summary sheet with check results
- Separate sheet per check with findings
- Review columns for manual verification
- Hebrew headers and content

## Legacy Comparison

When implementing or modifying checks:

1. Reference legacy script in `legacy/scripts/`
2. Compare output format and field names
3. Verify logic matches original
4. Test with same input data

```bash
# Run legacy for comparison
cd legacy/scripts
python mizrahi_special_transactions.py \
    --manager-name "סיגמא" \
    --output-dir "./debug_output"

# Compare with new implementation
diff -r legacy_output/ new_output/
```
