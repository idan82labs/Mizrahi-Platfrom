#!/bin/bash
#
# Test Hook 5 - K.303 Disclosure Validation via API
# Requires APIFY_API_TOKEN environment variable
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MANAGER="${1:-מגדל}"
EMAIL="${2:-test@test.com}"
API_URL="${API_URL:-http://localhost:8000}"

echo "=========================================="
echo "TEST: HOOK 5 - K.303 DISCLOSURE (via API)"
echo "=========================================="
echo "Manager: $MANAGER"
echo "Email: $EMAIL"
echo "API: $API_URL"
echo "=========================================="
echo ""

# Check if server is running
echo "[1/4] Checking API server..."
if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: API server not responding at $API_URL${NC}"
    echo "Start the server first: python server.py"
    exit 1
fi
echo -e "${GREEN}API server is running${NC}"
echo ""

# Send request
echo "[2/4] Sending K.303 disclosure report request..."
RESPONSE=$(curl -s -X POST "$API_URL/api/process-disclosure-report" \
    -F "manager_name=$MANAGER" \
    -F "email=$EMAIL")

JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
    echo -e "${RED}ERROR: Failed to start job${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "Job ID: $JOB_ID"
echo ""

# Poll for completion
echo "[3/4] Waiting for job completion..."
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    STATUS_RESPONSE=$(curl -s "$API_URL/api/job/$JOB_ID")
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
    MESSAGE=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', ''))" 2>/dev/null)

    echo "  Status: $STATUS - $MESSAGE"

    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo -e "${GREEN}Job completed successfully!${NC}"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo -e "${RED}Job failed!${NC}"
        echo "Error: $(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)"
        exit 1
    fi

    ATTEMPT=$((ATTEMPT + 1))
    sleep 5
done

if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
    echo -e "${YELLOW}WARNING: Job timed out after $((MAX_ATTEMPTS * 5)) seconds${NC}"
    exit 1
fi

# Get results
echo ""
echo "[4/4] Job Results:"
echo "=========================================="
echo "$STATUS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
result = data.get('result', {})
print(f\"Manager: {data.get('manager_name', 'N/A')}\")
print(f\"Report Month: {data.get('report_month', 'N/A')}\")
print(f\"Total Exceptions: {result.get('total_exceptions', 'N/A')}\")
print(f\"Output File: {result.get('output_file', 'N/A')}\")
print(f\"Email Sent To: {', '.join(result.get('email_sent_to', []))}\")
if 'check_results' in result:
    print('Check Results:')
    cr = result['check_results']
    print(f\"  - Check 1a (Fund Completeness): {cr.get('check_1a', 'N/A')}\")
    print(f\"  - Check 1b (Date Validity): {cr.get('check_1b', 'N/A')}\")
    print(f\"  - Check 2a (Previous Month): {cr.get('check_2a', 'N/A')}\")
    print(f\"  - Check 2b (Exposure Profile): {cr.get('check_2b', 'N/A')}\")
" 2>/dev/null || echo "$STATUS_RESPONSE"
echo "=========================================="
echo ""

echo -e "${GREEN}Test completed!${NC}"
