#!/bin/bash
#
# Run both hooks for all managers
# Usage: ./run_all_managers.sh
#        ./run_all_managers.sh --send-email
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

SEND_EMAIL=""
if [[ "$*" == *"--send-email"* ]]; then
    SEND_EMAIL="--send-email"
fi

echo "=========================================="
echo "MIZRAHI COMPLIANCE - ALL MANAGERS"
echo "=========================================="
echo "Processing all 10 fund managers"
echo "Output will be in: $SCRIPT_DIR/output"
echo "=========================================="
echo ""

# Check required environment variables
if [ -z "$APIFY_TOKEN" ]; then
    echo "ERROR: APIFY_TOKEN not set"
    echo "Set it in config/credentials.env or export it"
    exit 1
fi

# ==========================================
# HOOK 1: Monthly Report
# ==========================================
echo ""
echo "=========================================="
echo "STEP 1: HOOK 1 - MONTHLY REPORT"
echo "=========================================="
echo ""

python "$SCRIPT_DIR/scripts/batch_monthly_report.py" \
    --output-dir "$SCRIPT_DIR/output/hook1" \
    $SEND_EMAIL

# ==========================================
# HOOK 2: Special Transactions
# ==========================================
echo ""
echo "=========================================="
echo "STEP 2: HOOK 2 - SPECIAL TRANSACTIONS"
echo "=========================================="
echo ""

python "$SCRIPT_DIR/scripts/batch_special_transactions.py" \
    --apify-token "$APIFY_TOKEN" \
    --output-dir "$SCRIPT_DIR/output/hook2" \
    --skip-tase-prices \
    $SEND_EMAIL

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
echo "ALL PROCESSING COMPLETE"
echo "=========================================="
echo ""
echo "Hook 1 output: $SCRIPT_DIR/output/hook1/"
echo "Hook 2 output: $SCRIPT_DIR/output/hook2/"
echo ""
echo "=========================================="
