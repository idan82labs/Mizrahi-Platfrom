#!/bin/bash
#
# Run all hooks (1, 2, 5) for all managers
# Usage: ./run_all_managers.sh --email "your@email.com"
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

echo "=========================================="
echo "MIZRAHI COMPLIANCE - ALL MANAGERS"
echo "=========================================="
echo "Processing all 8 fund managers"
echo "=========================================="
echo ""

# ==========================================
# HOOK 1: Monthly Report
# ==========================================
echo ""
echo "=========================================="
echo "STEP 1: HOOK 1 - MONTHLY REPORT"
echo "=========================================="
echo ""

python "$SCRIPT_DIR/scripts/batch_hook1_with_email.py" "$@"

# ==========================================
# HOOK 2: Special Transactions
# ==========================================
echo ""
echo "=========================================="
echo "STEP 2: HOOK 2 - SPECIAL TRANSACTIONS"
echo "=========================================="
echo ""

python "$SCRIPT_DIR/scripts/batch_hook2_with_email.py" "$@"

# ==========================================
# HOOK 5: K.303 Disclosure
# ==========================================
echo ""
echo "=========================================="
echo "STEP 3: HOOK 5 - K.303 DISCLOSURE"
echo "=========================================="
echo ""

python "$SCRIPT_DIR/scripts/batch_hook5_with_email.py" "$@"

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
echo "ALL PROCESSING COMPLETE"
echo "=========================================="
