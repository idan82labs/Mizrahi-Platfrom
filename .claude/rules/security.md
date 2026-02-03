# Security Rules

CRITICAL: This is a regulatory compliance platform handling sensitive fund data.
Security violations could have legal consequences.

## Data Protection

### Never Log Sensitive Data

- Fund holdings data
- Transaction details
- Personal identifiable information (PII)
- API keys, tokens, passwords
- Hebrew content that might contain PII

### Never Expose in Error Messages

- Validation rules (could be gamed)
- Internal system paths
- Stack traces (in production)

## Input Validation

### Server-Side Validation Required

- All user input must be validated server-side
- Never trust client-side validation alone
- Validate file uploads (type, size, content)

## Secrets Management

### Environment Variables Only

- API keys (APIFY_API_TOKEN, RESEND_API_KEY)
- Secret keys

### Never Commit

- `.env` files
- `credentials.json`
- `*.pem` files
- Any file containing secrets

## Authentication & Authorization

### API Security

- Validate authentication on protected endpoints
- Use HTTPS only (in production)
- Implement rate limiting on public endpoints

### CORS Configuration

- Whitelist specific origins
- Never use wildcard (`*`) in production
- Configured in `deploy/digitalocean/server.py`

## File Operations

### File Uploads

- Validate MIME type (not just extension)
- Limit file size
- Use allowlist for permitted extensions

### File Paths

- Never construct paths from user input without sanitization
- Use `pathlib.Path` with strict validation
- Prevent path traversal attacks

## Audit Trail

### Log Security Events

- Hook executions
- Error occurrences (without sensitive data)

### Retention

- Keep audit logs for compliance requirements
- Include timestamp, action, result

## External Services

### Apify

- Token stored in environment variable
- Validate response data before processing
- Handle rate limits gracefully

### Resend (Email)

- API key in environment variable
- Validate recipient addresses
- Don't expose internal data in emails

## Code Review Checklist

Before committing, verify:

- [ ] No hardcoded secrets
- [ ] Input validation on all endpoints
- [ ] No command injection vulnerabilities
- [ ] Sensitive data not logged
- [ ] Error messages don't expose internals
- [ ] File operations are safe
