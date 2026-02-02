# Git Workflow

Branch strategy and commit conventions for the project.

## Branch Strategy

```
main (production)
  ↑ merges from dev only
dev (integration)
  ↑ merges from feature branches
feature/*, fix/*, etc.
  ↑ created from dev
```

## Protected Branches

### `main` (Production)
- NEVER commit directly
- NEVER push directly
- Only receives merges from `dev`
- Represents production-ready code

### `dev` (Integration)
- NEVER commit directly
- NEVER push directly
- Receives merges from feature branches
- Integration testing happens here

## Branch Types

| Type | Pattern | Created From | Merges To | Purpose |
|------|---------|--------------|-----------|---------|
| `feature/` | `feature/<description>` | `dev` | `dev` | New functionality |
| `fix/` | `fix/<description>` | `dev` | `dev` | Bug fixes |
| `hotfix/` | `hotfix/<description>` | `main` | `main` → `dev` | Urgent production fixes |
| `refactor/` | `refactor/<description>` | `dev` | `dev` | Code improvements |
| `docs/` | `docs/<description>` | `dev` | `dev` | Documentation only |
| `test/` | `test/<description>` | `dev` | `dev` | Test additions |
| `chore/` | `chore/<description>` | `dev` | `dev` | Build, deps, config |

## Branch Naming

### Rules
- Lowercase only
- Use hyphens to separate words (not underscores)
- Max 50 characters for description
- Be specific but concise

### Format
```
<type>/<description>
<type>/<ticket-id>-<description>
```

### Examples
```
feature/user-dashboard
feature/MIZ-123-add-validation
fix/login-error-handling
hotfix/critical-api-bug
refactor/hook-base-class
docs/api-reference
chore/update-dependencies
```

## Commit Messages

### Format (Conventional Commits)
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Formatting (no code change)
- `refactor` — Code change (no feature/fix)
- `perf` — Performance improvement
- `test` — Adding tests
- `chore` — Build, deps, config

### Scope (Optional)
- `api` — Backend changes
- `web` — Frontend changes
- `hooks` — Hooks package
- `shared` — Shared package
- `config` — Configuration

### Examples
```
feat(api): add hook execution endpoint
fix(hooks): correct price variance calculation
docs(api): update API reference
refactor(shared): simplify email service
test(hooks): add completeness check tests
chore: update Python dependencies
```

## Workflow

### Starting New Work
```bash
# Ensure you're on dev and up-to-date
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/my-feature
```

### Making Commits
```bash
# Stage changes
git add <files>

# Commit with conventional message
git commit -m "feat(scope): description"
```

### Before Creating PR
1. Run all tests
2. Fix TypeScript errors
3. Run linters
4. Update documentation if needed
5. Squash WIP commits

### Creating PR
```bash
# Push branch
git push -u origin feature/my-feature

# Create PR via GitHub
# Target: dev (not main!)
```

### Hotfix Process
```bash
# Create from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Fix and commit
git add .
git commit -m "hotfix: fix critical bug"

# Create PR to main
git push -u origin hotfix/critical-bug

# After merge to main, also merge to dev
git checkout dev
git merge main
git push origin dev
```

## Rules

### NEVER Do
- Commit directly to `main` or `dev`
- Force push to any branch
- Commit secrets or credentials
- Leave merge conflict markers
- Commit commented-out code

### ALWAYS Do
- Create branches from `dev` (except hotfixes)
- Use descriptive branch names
- Write meaningful commit messages
- Squash WIP commits before merge
- Delete branches after merge
