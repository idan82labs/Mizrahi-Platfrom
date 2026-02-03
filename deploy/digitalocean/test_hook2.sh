#!/bin/bash
#
# Test Hook 2 and compare with expected output
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
OUTPUT_DIR="$SCRIPT_DIR/output/test_hook2"

echo "=========================================="
echo "TESTING HOOK 2: SPECIAL TRANSACTIONS"
echo "=========================================="
echo "Manager: $MANAGER"
echo "Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Check APIFY_TOKEN
if [ -z "$APIFY_TOKEN" ]; then
    echo "ERROR: APIFY_TOKEN not set"
    echo "Set it in config/credentials.env"
    exit 1
fi

# Run hook for single manager
python "$SCRIPT_DIR/scripts/batch_special_transactions.py" \
    --apify-token "$APIFY_TOKEN" \
    --managers "$MANAGER" \
    --output-dir "$OUTPUT_DIR" \
    --skip-tase-prices

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""

# List output files
LATEST_OUTPUT=$(ls -td "$OUTPUT_DIR"/*/ 2>/dev/null | head -1)
if [ -n "$LATEST_OUTPUT" ]; then
    echo "Generated files:"
    ls -la "$LATEST_OUTPUT/$MANAGER/" 2>/dev/null || echo "No manager directory found"
fi
