---
description: Run full pre-commit verification (branch, types, lint, tests, security, docs)
allowed-tools: Bash, Read, Grep, Glob
---

Run the pre-commit-verification skill.

Execute all verification phases and produce a summary report:

1. **Branch Check** - Verify not on protected branch (main/dev)
2. **TypeScript Check** - Run `pnpm typecheck`, ensure 0 errors
3. **Linting** - Run `pnpm lint` and `uv run ruff check .`
4. **Tests** - Run appropriate tests based on change scope
5. **Security Scan** - Check for hardcoded secrets and debug statements
6. **Documentation Check** - Check if docs need updating based on changed files

After each phase, report status. Stop if critical issues found.

Produce final report:
```
╔══════════════════════════════════════╗
║     PRE-COMMIT VERIFICATION          ║
╠══════════════════════════════════════╣
║ Branch:       ✓/✗ [branch name]      ║
║ TypeScript:   ✓/✗ [error count]      ║
║ Linting:      ✓/✗ [issue count]      ║
║ Tests:        ✓/✗ [pass/fail count]  ║
║ Security:     ✓/✗ [findings]         ║
║ Documentation:✓/⚠ [status]           ║
╠══════════════════════════════════════╣
║ RESULT: READY / NOT READY            ║
╚══════════════════════════════════════╝
```
