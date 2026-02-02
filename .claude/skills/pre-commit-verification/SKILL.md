---
name: pre-commit-verification
description: |
  Pre-commit verification skill for Mizrahi project. Run before any commit
  to ensure code quality. Checks TypeScript errors, linting, tests, and
  documentation updates. Use with /verify command.
allowed-tools: Bash, Read, Grep, Glob
disable-model-invocation: true
---

# Pre-Commit Verification Skill

Run this verification before committing code.

## Verification Phases

Execute all phases in order. Stop and fix issues before proceeding.

### Phase 1: Branch Check

Verify you're NOT on a protected branch.

```bash
branch=$(git branch --show-current)
if [[ "$branch" == "main" || "$branch" == "dev" ]]; then
  echo "ERROR: Cannot commit on protected branch: $branch"
  echo "Create a feature branch first: git checkout -b feature/your-feature"
  exit 1
fi
echo "Branch: $branch ✓"
```

### Phase 2: TypeScript Check

All TypeScript errors must be resolved.

```bash
cd apps/web
pnpm typecheck
```

**Acceptance:** Exit code 0, no errors

### Phase 3: Linting

Run linters for both TypeScript and Python.

```bash
# TypeScript/JavaScript
pnpm lint

# Python
cd apps/api && uv run ruff check .
```

**Acceptance:** No errors (warnings acceptable but should be minimized)

### Phase 4: Tests

Run tests based on change scope.

```bash
# Determine change scope
changed_files=$(git diff --cached --name-only)

# Check if major change
is_major=false
echo "$changed_files" | grep -qE "^(packages/shared/|config/|apps/api/src/db/)" && is_major=true

if $is_major; then
  echo "Major change detected - running full test suite"
  cd apps/api && uv run pytest
else
  echo "Minor change - running targeted tests"
  # Run tests for changed modules
  cd apps/api && uv run pytest tests/ -x
fi
```

**Acceptance:** All tests pass

### Phase 5: Security Scan

Scan for security issues.

```bash
# Check for hardcoded secrets
git diff --cached | grep -iE "(api_key|secret|password|token).*=" && {
  echo "WARNING: Possible hardcoded secret detected!"
}

# Check for debug statements
git diff --cached --name-only | xargs grep -l "console\.log\|print(" 2>/dev/null | head -5
```

**Acceptance:** No secrets, minimal debug statements

### Phase 6: Documentation Check

Check if documentation needs updating.

```bash
changed_files=$(git diff --cached --name-only)

# Check if API changed
echo "$changed_files" | grep -q "apps/api/src/routers/" && {
  echo "REMINDER: API changed - check docs/api/API_REFERENCE.md"
}

# Check if hooks changed
echo "$changed_files" | grep -q "packages/hooks/" && {
  echo "REMINDER: Hooks changed - check docs/SYSTEM_DOCUMENTATION.md"
}

# Check if config changed
echo "$changed_files" | grep -q "config/" && {
  echo "REMINDER: Config changed - check relevant documentation"
}
```

### Phase 7: Git Status Review

Review what will be committed.

```bash
git status
git diff --cached --stat
```

## Report Format

After running all phases, produce a summary:

```
╔══════════════════════════════════════╗
║     PRE-COMMIT VERIFICATION          ║
╠══════════════════════════════════════╣
║ Branch Check:      ✓ PASS            ║
║ TypeScript:        ✓ PASS (0 errors) ║
║ Linting:           ✓ PASS            ║
║ Tests:             ✓ PASS (23/23)    ║
║ Security:          ✓ PASS            ║
║ Documentation:     ⚠ CHECK NEEDED    ║
╠══════════════════════════════════════╣
║ RESULT: READY TO COMMIT              ║
╚══════════════════════════════════════╝
```

## Quick Commands

```bash
# Full verification
pnpm typecheck && pnpm lint && pnpm test:py

# TypeScript only
pnpm typecheck

# Python only
cd apps/api && uv run ruff check . && uv run pytest
```

## Common Issues

### TypeScript Errors
- Missing type annotations
- Null/undefined not handled
- Import errors

### Linting Errors
- Unused imports
- Formatting issues
- Missing semicolons (TS)

### Test Failures
- Missing mocks
- Async timing issues
- Changed behavior not reflected in tests

## Bypassing (Emergency Only)

In emergencies, you can bypass with:
```bash
git commit --no-verify -m "hotfix: emergency fix"
```

**WARNING:** Only use for critical hotfixes. Always run verification afterward.
