#!/bin/bash
#
# Run Hook 2: Special Transactions Validation
# Usage: ./run_hook2.sh --email "your@email.com"
#        ./run_hook2.sh --managers "סיגמא,מגדל" --email "your@email.com"
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
echo "HOOK 2: SPECIAL TRANSACTIONS VALIDATION"
echo "=========================================="
echo ""

# Run batch processor (loads .env via python-dotenv)
python3 "$SCRIPT_DIR/scripts/batch_hook2_with_email.py" "$@"

echo ""
echo "=========================================="
echo "HOOK 2 COMPLETE"
echo "=========================================="
