# Agent Delegation Rules - Legacy Hosting

When to delegate tasks to specialized subagents.

## When to Delegate

### Security Review

- API endpoint modifications
- Input validation code
- File upload handling
- Any code touching sensitive data

Use: `security-reviewer` agent

### Code Review — Before Major Changes

- Significant refactoring
- Multiple file changes

Use: `code-reviewer` agent

### Planning — For Complex Tasks

- Features touching 3+ files
- Architecture decisions

Use: `planner` agent

## When NOT to Delegate

### Simple Tasks

- Single-file edits
- Typo fixes
- Configuration tweaks
- Simple bug fixes

### Quick Changes

- Documentation updates
- Dependency updates

### Trivial Operations

- Import organization
- Formatting fixes
- Renaming variables

## Agent Summary

| Agent               | Model  | Use For                        |
| ------------------- | ------ | ------------------------------ |
| `planner`           | opus   | Multi-file planning            |
| `code-reviewer`     | sonnet | Quality review, best practices |
| `security-reviewer` | sonnet | Security vulnerabilities       |
