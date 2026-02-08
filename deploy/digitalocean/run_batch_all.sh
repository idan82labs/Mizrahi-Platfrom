#!/bin/bash
# Run unified batch processing for all hooks (Hook 1, Hook 2, Hook 5)
#
# Usage:
#   ./run_batch_all.sh                          # Process all managers (dry run)
#   ./run_batch_all.sh --send-email             # Process all and send emails
#   ./run_batch_all.sh --managers "מגדל,סיגמא"   # Process specific managers
#
# Environment Variables Required:
#   APIFY_API_TOKEN - For fetching data from Maya TASE
#   RESEND_API_KEY  - For sending emails (only if --send-email flag is used)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "/opt/mizrahi/venv" ]; then
    source /opt/mizrahi/venv/bin/activate
fi

# Check for APIFY_API_TOKEN
if [ -z "$APIFY_API_TOKEN" ]; then
    echo "ERROR: APIFY_API_TOKEN environment variable is required"
    echo "Usage: export APIFY_API_TOKEN='your_token' && ./run_batch_all.sh"
    exit 1
fi

# Run the batch processor
python3 scripts/batch_all_hooks.py "$@"
