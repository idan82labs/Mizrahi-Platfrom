#!/bin/bash
#
# Test Hook 2: Special Transactions for a single manager
# Usage: ./test_hook2.sh [MANAGER]
#
# Environment: Loads .env via python-dotenv (needs APIFY_API_TOKEN)
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
OUTPUT_DIR="$SCRIPT_DIR/output/test_hook2"

echo "=========================================="
echo "TESTING HOOK 2: SPECIAL TRANSACTIONS"
echo "=========================================="
echo "Manager: $MANAGER"
echo "Output: $OUTPUT_DIR"
echo "=========================================="
echo ""

# Run hook for single manager (no email sending)
python3 "$SCRIPT_DIR/scripts/batch_hook2_with_email.py" \
    --managers "$MANAGER" \
    --email "test@test.com" \
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
