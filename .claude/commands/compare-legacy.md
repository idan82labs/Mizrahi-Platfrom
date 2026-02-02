---
description: Compare new implementation with legacy scripts
allowed-tools: Read, Grep, Glob, Bash
---

Compare implementation with legacy: $ARGUMENTS

Use the legacy-validator agent to compare.

## Process

1. **Identify Target**
   - If argument is a hook name: compare entire hook
   - If argument is a check name: compare specific check
   - If no argument: show available comparisons

2. **Legacy File Mapping**
   | Hook | Legacy Script |
   |------|--------------|
   | monthly_report | legacy/scripts/fund_automation_complete.py |
   | special_transactions | legacy/scripts/mizrahi_special_transactions.py |

3. **Check Function Mapping (special_transactions)**
   | Check | Legacy Function |
   |-------|----------------|
   | duplicates | check_1_duplicates() |
   | dates | check_3_date_validation() |
   | decision_method | check_4_decision_method() |
   | sampling | check_5_sampling() |
   | prices | check_6_tase_prices() |
   | problematic_securities | check_7_problematic_securities() |

4. **Comparison Points**
   - Input handling
   - Validation logic
   - Output format (CheckResult vs dict)
   - Field names (especially Hebrew)
   - Constants (asset types, thresholds)
   - Error handling

5. **Report**
   ```
   # Legacy Comparison: <target>

   ## Logic Comparison
   | Aspect | Legacy | New | Match? |
   |--------|--------|-----|--------|

   ## Constants Verification
   | Constant | Legacy Value | New Value | Match? |
   |----------|--------------|-----------|--------|

   ## Differences Found
   1. [Description]

   ## Recommendations
   - [Action items]

   ## Status: [MATCHES / DIFFERENCES FOUND]
   ```
