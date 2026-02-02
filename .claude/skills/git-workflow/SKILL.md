---
name: git-workflow
description: |
  Git workflow enforcement for Mizrahi project. Use when creating branches,
  making commits, or preparing pull requests. Enforces main←dev←feature
  branch strategy with protected branches.
allowed-tools: Bash, Read, Grep
---

# Git Workflow Skill

Enforces the project's branch strategy: `main` ← `dev` ← feature branches.

## Branch Rules

### Protected Branches (NEVER commit/push directly)
- `main` — Production branch, receives merges from `dev` only
- `dev` — Integration branch, receives merges from feature branches

### Feature Branch Flow
1. Always create branches from `dev`
2. Use proper naming convention
3. Merge back to `dev` via PR
4. `dev` gets merged to `main` for releases

## Branch Naming Convention

Format: `<type>/<description>` or `<type>/<ticket>-<description>`

| Type | Purpose | Example |
|------|---------|---------|
| `feature/` | New functionality | `feature/user-dashboard` |
| `fix/` | Bug fixes | `fix/validation-error` |
| `hotfix/` | Urgent production fixes | `hotfix/critical-bug` |
| `refactor/` | Code improvements | `refactor/hook-cleanup` |
| `docs/` | Documentation | `docs/api-reference` |
| `test/` | Test additions | `test/hook-coverage` |
| `chore/` | Build, deps, config | `chore/update-deps` |

### Naming Rules
- Lowercase only
- Hyphens between words (no underscores)
- Max 50 characters for description
- Be specific but concise

## Creating a New Branch

```bash
# 1. Ensure you're on dev and up-to-date
git checkout dev
git pull origin dev

# 2. Create and switch to new branch
git checkout -b feature/my-feature-name

# 3. Verify
git branch --show-current
```

## Commit Messages (Conventional Commits)

Format: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Scopes: `api`, `web`, `hooks`, `shared`, `config`

Examples:
```
feat(api): add hook execution endpoint
fix(hooks): correct price variance calculation
docs: update API reference
chore: update dependencies
```

## Before Creating PR

1. Ensure all tests pass
2. Fix all TypeScript errors
3. Run linters
4. Squash WIP commits if needed
5. Target `dev` branch (not `main`!)

## Hotfix Process (from main)

Only for urgent production issues:

```bash
# Create from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue

# After fix, create PR to main
# Then merge main back to dev
```

## Verification Commands

```bash
# Check current branch
git branch --show-current

# Check if on protected branch
branch=$(git branch --show-current)
if [[ "$branch" == "main" || "$branch" == "dev" ]]; then
  echo "WARNING: On protected branch!"
fi

# Check uncommitted changes
git status

# Check unpushed commits
git log origin/$(git branch --show-current)..HEAD
```
