# Agent Delegation Rules

When to delegate tasks to specialized subagents.

## When to Delegate

### Security Review — ALWAYS Delegate
- Authentication/authorization changes
- Input validation code
- API endpoint modifications
- File upload handling
- Any code touching sensitive data

Use: `security-reviewer` agent

### Code Review — Before PRs
- Completed features before creating PR
- After significant refactoring
- Before merging to `dev`

Use: `code-reviewer` agent

### Planning — For Complex Tasks
- Features touching 3+ files
- Architecture decisions
- Refactoring strategies
- Database schema changes

Use: `planner` agent

### Test Writing — For New Features
- New hook implementations
- New check functions
- API endpoint additions
- Complex business logic

Use: `test-writer` agent

### Legacy Comparison — When Modifying Hooks
- Implementing new checks
- Modifying existing check logic
- Debugging output differences

Use: `legacy-validator` agent

## When NOT to Delegate

### Simple Tasks
- Single-file edits
- Typo fixes
- Comment updates
- Simple bug fixes with obvious solution

### Quick Changes
- Adding a single test
- Configuration tweaks
- Documentation updates
- Dependency updates

### Trivial Operations
- Import organization
- Formatting fixes
- Renaming variables

## Delegation Patterns

### Security-Sensitive Code
```
Before writing auth/security code:
1. Delegate to security-reviewer for review of existing code
2. Implement changes
3. Delegate to security-reviewer for review of changes
```

### Major Feature
```
1. Delegate to planner for implementation plan
2. Review and approve plan
3. Implement step by step
4. Delegate to test-writer for tests
5. Delegate to code-reviewer before PR
```

### Hook Modification
```
1. Delegate to legacy-validator to understand original behavior
2. Implement changes
3. Delegate to legacy-validator to compare outputs
4. Delegate to test-writer for new tests
```

## Agent Summary

| Agent | Model | Use For |
|-------|-------|---------|
| `planner` | opus | Architecture, multi-file planning |
| `code-reviewer` | sonnet | Quality review, best practices |
| `security-reviewer` | sonnet | Security vulnerabilities |
| `test-writer` | sonnet | Test generation |
| `legacy-validator` | haiku | Compare with legacy scripts |
