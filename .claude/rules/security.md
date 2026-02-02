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
- Database queries
- Stack traces (in production)

## Input Validation

### Server-Side Validation Required
- All user input must be validated server-side
- Never trust client-side validation alone
- Use Pydantic models for request validation
- Validate file uploads (type, size, content)

### SQL/NoSQL Injection Prevention
- Always use parameterized queries
- Never use string concatenation for queries
- Use ORM methods (SQLModel/SQLAlchemy)

```python
# Correct
stmt = select(User).where(User.id == user_id)

# NEVER DO THIS
query = f"SELECT * FROM users WHERE id = {user_id}"
```

## Secrets Management

### Environment Variables Only
- API keys (APIFY_API_TOKEN, RESEND_API_KEY)
- Database credentials
- Secret keys

### Never Commit
- `.env` files
- `credentials.json`
- `*.pem` files
- Any file containing secrets

### Git Pre-commit Check
- Scan for hardcoded secrets before commit
- Block commits containing API keys or passwords

## Authentication & Authorization

### API Security
- Validate authentication on all protected endpoints
- Check authorization for resource access
- Use HTTPS only (in production)
- Implement rate limiting on public endpoints

### CORS Configuration
- Whitelist specific origins
- Never use wildcard (`*`) in production
- Configured in `apps/api/src/main.py`

## File Operations

### File Uploads
- Validate MIME type (not just extension)
- Limit file size
- Use allowlist for permitted extensions
- Scan for malicious content

### File Paths
- Never construct paths from user input without sanitization
- Use `pathlib.Path` with strict validation
- Prevent path traversal attacks

## Audit Trail

### Log Security Events
- Authentication attempts
- Hook executions
- Configuration changes
- Error occurrences (without sensitive data)

### Retention
- Keep audit logs for compliance requirements
- Include timestamp, user, action, result

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

Before merging, verify:
- [ ] No hardcoded secrets
- [ ] Input validation on all endpoints
- [ ] No SQL/command injection vulnerabilities
- [ ] Sensitive data not logged
- [ ] Error messages don't expose internals
- [ ] File operations are safe
- [ ] Authentication/authorization implemented
