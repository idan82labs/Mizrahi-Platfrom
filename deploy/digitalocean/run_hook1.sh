#!/bin/bash
#
# Run Hook 1: Monthly Report Validation
# Usage: ./run_hook1.sh --email "your@email.com"
#        ./run_hook1.sh --managers "סיגמא,מגדל" --email "your@email.com"
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
echo "HOOK 1: MONTHLY REPORT VALIDATION"
echo "=========================================="
echo ""

# Run batch processor (loads .env via python-dotenv)
python3 "$SCRIPT_DIR/scripts/batch_hook1_with_email.py" "$@"

echo ""
echo "=========================================="
echo "HOOK 1 COMPLETE"
echo "=========================================="
