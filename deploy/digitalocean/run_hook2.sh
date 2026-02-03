#!/bin/bash
#
# Run Hook 2: Special Transactions Validation
# Usage: ./run_hook2.sh --manager "סיגמא"
#        ./run_hook2.sh --all --send-email
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load credentials if available
if [ -f "$SCRIPT_DIR/config/credentials.env" ]; then
    source "$SCRIPT_DIR/config/credentials.env"
fi

# Activate virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
elif [ -d "/root/mizrahi-venv" ]; then
    source /root/mizrahi-venv/bin/activate
fi

echo "=========================================="
echo "HOOK 2: SPECIAL TRANSACTIONS VALIDATION"
echo "=========================================="
echo ""

# Check if APIFY_TOKEN is set
if [ -z "$APIFY_TOKEN" ]; then
    echo "ERROR: APIFY_TOKEN not set"
    echo "Set it in config/credentials.env or export it:"
    echo "  export APIFY_TOKEN=your_token_here"
    exit 1
fi

# Run batch processor
python "$SCRIPT_DIR/scripts/batch_special_transactions.py" \
    --apify-token "$APIFY_TOKEN" \
    --output-dir "$SCRIPT_DIR/output/hook2" \
    --skip-tase-prices \
    "$@"

echo ""
echo "=========================================="
echo "HOOK 2 COMPLETE"
echo "=========================================="
