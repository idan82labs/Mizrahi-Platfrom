#!/bin/bash
#
# Run Hook 5: K.303 Disclosure Validation
# Usage: ./run_hook5.sh --email "your@email.com"
#        ./run_hook5.sh --managers "מגדל,הראל" --email "your@email.com"
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
echo "HOOK 5: K.303 DISCLOSURE VALIDATION"
echo "=========================================="
echo ""

# Run batch processor (loads .env via python-dotenv)
python3 "$SCRIPT_DIR/scripts/batch_hook5_with_email.py" "$@"

echo ""
echo "=========================================="
echo "HOOK 5 COMPLETE"
echo "=========================================="
