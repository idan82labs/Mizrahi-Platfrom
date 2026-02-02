#!/bin/bash
# Development startup script

set -e

echo "Starting Mizrahi Compliance Platform (Development)..."

# Check for required tools
command -v pnpm >/dev/null 2>&1 || { echo "pnpm is required but not installed."; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "uv is required but not installed."; exit 1; }

# Start frontend in background
echo "Starting frontend..."
(cd apps/web && pnpm dev) &
FRONTEND_PID=$!

# Start API
echo "Starting API..."
(cd apps/api && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000) &
API_PID=$!

# Trap to clean up background processes
cleanup() {
    echo "Shutting down..."
    kill $FRONTEND_PID 2>/dev/null
    kill $API_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo ""
echo "Services started:"
echo "  Frontend: http://localhost:5173"
echo "  API:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
