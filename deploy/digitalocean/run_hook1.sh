#!/bin/bash
#
# Run Hook 1: Monthly Report Validation
# Usage: ./run_hook1.sh --fund-name "סיגמא"
#        ./run_hook1.sh --fund-name "סיגמא" --send-email
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
echo "HOOK 1: MONTHLY REPORT VALIDATION"
echo "=========================================="
echo ""

# Run the script
python "$SCRIPT_DIR/scripts/fund_automation_complete.py" "$@"

echo ""
echo "=========================================="
echo "HOOK 1 COMPLETE"
echo "=========================================="
