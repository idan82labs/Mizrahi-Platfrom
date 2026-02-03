# Testing Rules - Legacy Hosting

Guidelines for testing the legacy deployment.

## Test Methods

### Manual Testing (Primary)

For standalone Python scripts, use the test scripts:

```bash
cd deploy/digitalocean

# Test Hook 2 offline (no Apify needed)
./test_offline_hook2.sh סיגמא

# Test Hook 1 (requires Apify token)
./test_hook1.sh סיגמא
```

### API Testing

Test the FastAPI server endpoints:

```bash
# Start server
cd deploy/digitalocean
python server.py

# Test health endpoint
curl http://localhost:8000/

# Test managers endpoint
curl http://localhost:8000/api/managers

# Test Hook 2
curl -X POST http://localhost:8000/api/process-report \
  -H "Content-Type: application/json" \
  -d '{"manager_name": "סיגמא", "email": "test@test.com"}'

# Test Hook 1
curl -X POST http://localhost:8000/api/process-monthly-report \
  -H "Content-Type: application/json" \
  -d '{"manager_name": "סיגמא", "email": "test@test.com"}'
```

### Frontend Testing

```bash
cd frontend
npm run dev
# Open http://localhost:5173
```

## Test Data

Test data files are located in:

- `deploy/digitalocean/test_data/` - Sample manager reports and Magna files

## What to Test

### Before Committing

- Server starts without errors
- Health endpoint responds
- Managers endpoint returns correct data
- Hook endpoints accept requests

### Before Deployment

- Full hook execution with test manager
- Report generation completes
- Email sending (if enabled)

## TypeScript Errors (Frontend)

All TypeScript errors must be fixed before commit:

```bash
cd frontend
npm run build
```

Build failures indicate TypeScript errors that need fixing.
