# CRITICAL: Legacy Branch Warning

> **THIS IS THE `legacy/digitalocean-hosting` BRANCH**
>
> **DO NOT merge this branch into `dev` or `main`.**
>
> This branch is maintained separately for standalone Digital Ocean deployment
> and has a completely different architecture from the main codebase.

## Branch Purpose

This branch contains:

- Standalone FastAPI server (`deploy/digitalocean/server.py`)
- Legacy Python scripts for hook processing
- React frontend (`frontend/`)
- YAML configuration files

## What's Different

- **No monorepo architecture** - no `apps/api/` or `packages/`
- **Standalone scripts** - not a modular hook system
- **Direct deployment** - runs on Digital Ocean droplet
- **Simplified structure** - frontend + deployment code only

## Allowed Operations

You MAY:

- Make fixes and updates on this branch
- Commit changes for bug fixes and improvements
- Update documentation for legacy hosting

You must NEVER:

- Create PRs targeting `dev` or `main`
- Suggest merging this branch into other branches
- Reference non-existent monorepo code paths
