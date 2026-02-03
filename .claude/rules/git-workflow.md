# Git Workflow - Legacy Branch

> **CRITICAL WARNING**: This is the `legacy/digitalocean-hosting` branch.
> **DO NOT merge this branch into `dev` or `main`**.
> This branch is maintained separately for standalone Digital Ocean deployment.

## Legacy Branch Rules

### NEVER Merge to Main Branches

This branch (`legacy/digitalocean-hosting`) must **NEVER** be merged into:

- `main` (production)
- `dev` (integration)

This is a standalone legacy deployment that differs significantly from the main codebase architecture.

### Allowed Operations

- Make fixes and updates directly on this branch
- Commit changes for bug fixes and improvements
- Keep the deployment working and up-to-date

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
- `chore` — Build, deps, config

### Scope (Optional for Legacy)

- `server` — FastAPI server changes
- `hook1` — Hook 1 (Monthly Report)
- `hook2` — Hook 2 (Special Transactions)
- `frontend` — Frontend changes
- `config` — Configuration changes

### Examples

```
fix(hook2): correct event ID for special transactions
feat(server): add monthly report endpoint
docs: update README for legacy hosting
chore: update Python dependencies
```

## Making Changes

### Direct Commits (Allowed on Legacy)

```bash
# Make changes
git add <files>
git commit -m "fix(server): description"
git push origin legacy/digitalocean-hosting
```

### For Complex Changes

```bash
# Create a sub-branch
git checkout -b legacy/fix-something
# Make changes
git add .
git commit -m "fix: description"
# Merge back to legacy branch
git checkout legacy/digitalocean-hosting
git merge legacy/fix-something
git branch -d legacy/fix-something
git push origin legacy/digitalocean-hosting
```

## Rules

### NEVER Do

- Merge into `main` or `dev`
- Create PRs targeting `main` or `dev`
- Commit secrets or credentials
- Leave merge conflict markers

### ALWAYS Do

- Keep changes isolated to this branch
- Test deployments before committing
- Update documentation when making changes
- Use descriptive commit messages
