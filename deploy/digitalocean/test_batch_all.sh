#!/bin/bash
# Test unified batch processing with a single manager (dry run)
#
# This script tests the batch_all_hooks.py with one manager (סיגמא)
# without sending emails. Use this to verify the batch processor works
# before running a full batch with email sending.
#
# Usage:
#   ./test_batch_all.sh                     # Test with סיגמא (default)
#   ./test_batch_all.sh מגדל                # Test with specific manager
#
# Environment Variables Required:
#   APIFY_API_TOKEN - For fetching data from Maya TASE

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default manager for testing
MANAGER="${1:-סיגמא}"

echo "=================================================="
echo "TESTING BATCH ALL HOOKS"
echo "=================================================="
echo "Manager: $MANAGER"
echo "Output: ./test_output"
echo "Email: disabled (dry run)"
echo "=================================================="

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

# Check for APIFY_API_TOKEN
if [ -z "$APIFY_API_TOKEN" ]; then
    echo ""
    echo "ERROR: APIFY_API_TOKEN environment variable is required"
    echo ""
    echo "Set it with:"
    echo "  export APIFY_API_TOKEN='your_token'"
    echo ""
    exit 1
fi

# Run test
python scripts/batch_all_hooks.py \
    --managers "$MANAGER" \
    --output-dir ./test_output

echo ""
echo "=================================================="
echo "TEST COMPLETE"
echo "=================================================="
echo "Check output in: ./test_output/"
echo ""
echo "To send test email, run:"
echo "  export RESEND_API_KEY='your_key'"
echo "  python scripts/batch_all_hooks.py --managers \"$MANAGER\" --email \"your@email.com\" --send-email"
echo ""
