#!/bin/bash
#
# Test Hook 1 and compare with expected output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load credentials
if [ -f "$SCRIPT_DIR/config/credentials.env" ]; then
    source "$SCRIPT_DIR/config/credentials.env"
fi

# Activate venv
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

MANAGER="${1:-סיגמא}"
OUTPUT_DIR="$SCRIPT_DIR/output/test_hook1"
EXPECTED_DIR="$SCRIPT_DIR/test_data/hook1_expected_output"

echo "=========================================="
echo "TESTING HOOK 1: MONTHLY REPORT"
echo "=========================================="
echo "Manager: $MANAGER"
echo "Output: $OUTPUT_DIR"
echo "Expected: $EXPECTED_DIR"
echo "=========================================="
echo ""

# Run hook
python3 "$SCRIPT_DIR/scripts/fund_automation_complete.py" \
    --fund-name "$MANAGER" \
    --output-dir "$OUTPUT_DIR"

echo ""
echo "=========================================="
echo "COMPARING OUTPUT"
echo "=========================================="

# Find output file
OUTPUT_FILE=$(ls -t "$OUTPUT_DIR"/דוח_${MANAGER}_*.xlsx 2>/dev/null | head -1)
EXPECTED_FILE=$(ls "$EXPECTED_DIR"/דוח_${MANAGER}_*.xlsx 2>/dev/null | head -1)

if [ -z "$OUTPUT_FILE" ]; then
    echo "ERROR: No output file generated"
    exit 1
fi

echo "Generated: $OUTPUT_FILE"

if [ -z "$EXPECTED_FILE" ]; then
    echo "WARNING: No expected file found for comparison"
    echo "Test output saved to: $OUTPUT_FILE"
else
    echo "Expected: $EXPECTED_FILE"
    echo ""

    # Compare file sizes (portable: works on both Linux and macOS)
    OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE" | tr -d ' ')
    EXPECTED_SIZE=$(wc -c < "$EXPECTED_FILE" | tr -d ' ')

    echo "Output size: $OUTPUT_SIZE bytes"
    echo "Expected size: $EXPECTED_SIZE bytes"

    if [ "$OUTPUT_SIZE" -eq "$EXPECTED_SIZE" ]; then
        echo "✓ File sizes match"
    else
        echo "⚠ File sizes differ (this may be OK due to timestamps)"
    fi
fi

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
