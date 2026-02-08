#!/bin/bash
# Test unified batch processing with a single manager (dry run)
#
# Usage:
#   ./test_batch_all.sh "your@email.com"                    # Test with סיגמא (default)
#   ./test_batch_all.sh "your@email.com" מגדל               # Test with specific manager
#
# Environment Variables Required:
#   APIFY_API_TOKEN - For fetching data from Maya TASE

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

EMAIL="${1:?Usage: ./test_batch_all.sh EMAIL [MANAGER]}"
MANAGER="${2:-סיגמא}"

echo "=================================================="
echo "TESTING BATCH ALL HOOKS"
echo "=================================================="
echo "Manager: $MANAGER"
echo "Email: $EMAIL"
echo "Output: ./test_output"
echo "Email sending: disabled (no --send-email flag)"
echo "=================================================="

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

# Run test (loads .env via python-dotenv)
python3 scripts/batch_all_hooks.py \
    --managers "$MANAGER" \
    --email "$EMAIL" \
    --output-dir ./test_output

echo ""
echo "=================================================="
echo "TEST COMPLETE"
echo "=================================================="
echo "Check output in: ./test_output/"
echo ""
echo "To send emails, add --send-email flag:"
echo "  python scripts/batch_all_hooks.py --managers \"$MANAGER\" --email \"$EMAIL\" --send-email"
echo ""
