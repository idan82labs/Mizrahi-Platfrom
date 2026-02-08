#!/bin/bash
#
# Offline Test Hook 2 - Uses existing test data (no Apify calls)
# Compares output with legacy expected results
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

MANAGER="${1:-סיגמא}"
TEST_DATA_DIR="$SCRIPT_DIR/test_data/hook2_legacy_complete"
OUTPUT_DIR="$SCRIPT_DIR/output/test_comparison"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "=========================================="
echo "OFFLINE TEST: HOOK 2 - SPECIAL TRANSACTIONS"
echo "=========================================="
echo "Manager: $MANAGER"
echo "Test Data: $TEST_DATA_DIR"
echo "Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Check test data exists
if [ ! -f "$TEST_DATA_DIR/Mutual_Funds_List.xlsx" ]; then
    echo "ERROR: Test data not found at $TEST_DATA_DIR"
    echo "Expected files:"
    echo "  - Mutual_Funds_List.xlsx"
    echo "  - <manager>/<manager>_special_transactions.csv"
    exit 1
fi

# Check manager test data
MANAGER_CSV="$TEST_DATA_DIR/$MANAGER/${MANAGER}_special_transactions.csv"
if [ ! -f "$MANAGER_CSV" ]; then
    echo "ERROR: Manager test data not found: $MANAGER_CSV"
    echo "Available managers:"
    ls -d "$TEST_DATA_DIR"/*/ 2>/dev/null | xargs -n1 basename
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR/$MANAGER"

echo "[1/3] Running mizrahi_special_transactions.py with test data..."
echo ""

# Run the processing script directly (no Apify)
SPEC_FILE="$TEST_DATA_DIR/Special_Transactions_Specifications.xlsx"
SPEC_ARG=""
if [ -f "$SPEC_FILE" ]; then
    SPEC_ARG="--spec-file $SPEC_FILE"
    echo "Using spec file: $SPEC_FILE"
fi

python3 "$SCRIPT_DIR/scripts/mizrahi_special_transactions.py" \
    --mutual-funds-list "$TEST_DATA_DIR/Mutual_Funds_List.xlsx" \
    --input-report "$MANAGER_CSV" \
    --output-xlsx "$OUTPUT_DIR/$MANAGER/${MANAGER}_special_transactions_report.xlsx" \
    --email-json "$OUTPUT_DIR/$MANAGER/${MANAGER}_email.json" \
    --manager-name "$MANAGER" \
    --skip-tase-prices \
    --price-threshold 5.0 \
    $SPEC_ARG

echo ""
echo "[2/3] Comparing output with legacy expected results..."
echo ""

# Compare with legacy output
python3 "$SCRIPT_DIR/scripts/compare_output.py" \
    --new-dir "$OUTPUT_DIR" \
    --legacy-dir "$TEST_DATA_DIR" \
    --manager "$MANAGER" \
    --output-json "$OUTPUT_DIR/comparison_${MANAGER}_${TIMESTAMP}.json"

COMPARE_EXIT=$?

echo ""
echo "=========================================="
if [ $COMPARE_EXIT -eq 0 ]; then
    echo "TEST PASSED: Output matches legacy!"
else
    echo "TEST FAILED: Output differs from legacy"
fi
echo "=========================================="
echo ""
echo "Output files:"
ls -la "$OUTPUT_DIR/$MANAGER/" 2>/dev/null || echo "No output files"
echo ""
echo "Comparison report: $OUTPUT_DIR/comparison_${MANAGER}_${TIMESTAMP}.json"

exit $COMPARE_EXIT
