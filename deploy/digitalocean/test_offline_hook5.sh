#!/bin/bash
#
# Offline Test Hook 5 - K.303 Disclosure Validation
# Uses existing test data (no Apify calls)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

MANAGER="${1:-מגדל}"
REPORT_MONTH="${2:-$(date +"%Y-%m")}"
TEST_DATA_DIR="$SCRIPT_DIR/test_data/hook5"
OUTPUT_DIR="$SCRIPT_DIR/output/hook5_test"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "=========================================="
echo "OFFLINE TEST: HOOK 5 - K.303 DISCLOSURE"
echo "=========================================="
echo "Manager: $MANAGER"
echo "Report Month: $REPORT_MONTH"
echo "Test Data: $TEST_DATA_DIR"
echo "Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Check test data exists
MUTUAL_FUNDS_FILE="$TEST_DATA_DIR/Mutual_Funds_List.xlsx - Worksheet.csv"
if [ ! -f "$MUTUAL_FUNDS_FILE" ]; then
    echo "ERROR: Mutual funds list not found at $TEST_DATA_DIR"
    echo "Expected file: Mutual_Funds_List.xlsx - Worksheet.csv"
    exit 1
fi

# For testing, we use the previous month file as both current and previous
CURRENT_REPORT="$TEST_DATA_DIR/disclosure_migdal_previous_month.xlsx - Sheet1.csv"
PREVIOUS_REPORT="$TEST_DATA_DIR/disclosure_migdal_previous_month.xlsx - Sheet1.csv"

if [ ! -f "$CURRENT_REPORT" ]; then
    echo "ERROR: Current report not found: $CURRENT_REPORT"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "[1/2] Running disclosure_k303_validator.py with test data..."
echo ""

# Check for spec file
SPEC_FILE="$TEST_DATA_DIR/בדיקת דוח גילוי נאות ק.303.xlsx - גיליון1.csv"
SPEC_ARG=""
if [ -f "$SPEC_FILE" ]; then
    SPEC_ARG="--spec-file \"$SPEC_FILE\""
    echo "Using spec file: $SPEC_FILE"
fi

# Run the K.303 validator
python "$SCRIPT_DIR/scripts/disclosure_k303_validator.py" \
    --mutual-funds-list "$MUTUAL_FUNDS_FILE" \
    --current-report "$CURRENT_REPORT" \
    --previous-report "$PREVIOUS_REPORT" \
    --output-xlsx "$OUTPUT_DIR/k303_${MANAGER}_${TIMESTAMP}.xlsx" \
    --report-month "$REPORT_MONTH" \
    --manager-name "$MANAGER" \
    --spec-file "$SPEC_FILE"

VALIDATION_EXIT=$?

echo ""
echo "=========================================="
if [ $VALIDATION_EXIT -eq 0 ]; then
    echo "TEST PASSED: Validation completed successfully!"
else
    echo "TEST FAILED: Validation encountered errors"
fi
echo "=========================================="
echo ""
echo "Output files:"
ls -la "$OUTPUT_DIR/" 2>/dev/null | tail -5
echo ""

exit $VALIDATION_EXIT
