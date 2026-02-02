---
name: documentation-check
description: |
  Documentation check skill for Mizrahi project. Use before commits to check
  if documentation needs updating based on changed files. Includes documentation
  register for quick lookup.
allowed-tools: Read, Grep, Glob, Bash
---

# Documentation Check Skill

Ensures documentation stays in sync with code changes.

## Documentation Register

Quick reference for which docs cover which areas:

| Area | Documentation File | Update When |
|------|-------------------|-------------|
| **API Endpoints** | `docs/api/API_REFERENCE.md` | Adding/modifying API routes |
| **Hook System** | `docs/guides/HOOKS_DEVELOPMENT.md` | Hook architecture changes |
| **New Hooks** | `docs/SYSTEM_DOCUMENTATION.md` | Adding new hooks |
| **Check Functions** | `docs/SYSTEM_DOCUMENTATION.md` | Adding new checks |
| **Configuration** | `docs/guides/DEVELOPMENT.md` | Config file changes |
| **Architecture** | `docs/ARCHITECTURE.md` | Major structural changes |
| **Setup** | `docs/guides/DEVELOPMENT.md` | Setup/install changes |
| **Commands** | `docs/CHEATSHEET.md` | New CLI commands |
| **Batch Processing** | `docs/guides/BATCH_PROCESSING.md` | Batch workflow changes |
| **Legacy Reference** | `docs/reference/LEGACY_FILES_REFERENCE.md` | Legacy file changes |

## Decision Flow

### Check if Docs Need Update

```
Changed files include apps/api/src/routers/*?
├── Yes → Update API_REFERENCE.md
└── No → Continue...

Changed files include packages/hooks/*?
├── Yes → Check HOOKS_DEVELOPMENT.md, SYSTEM_DOCUMENTATION.md
└── No → Continue...

Changed files include config/*?
├── Yes → Check DEVELOPMENT.md, relevant hook docs
└── No → Continue...

Added new hook or check?
├── Yes → Update SYSTEM_DOCUMENTATION.md
└── No → Continue...

Changed setup/install process?
├── Yes → Update DEVELOPMENT.md, README.md
└── No → No docs update needed
```

## File Pattern to Doc Mapping

```python
DOC_MAPPING = {
    "apps/api/src/routers/": ["docs/api/API_REFERENCE.md"],
    "apps/api/src/main.py": ["docs/api/API_REFERENCE.md"],
    "packages/hooks/src/mizrahi_hooks/*/hook.py": [
        "docs/SYSTEM_DOCUMENTATION.md",
        "docs/guides/HOOKS_DEVELOPMENT.md"
    ],
    "packages/hooks/src/mizrahi_hooks/*/checks/": [
        "docs/SYSTEM_DOCUMENTATION.md"
    ],
    "config/hooks.yaml": [
        "docs/SYSTEM_DOCUMENTATION.md",
        "docs/guides/DEVELOPMENT.md"
    ],
    "config/managers.yaml": [
        "docs/SYSTEM_DOCUMENTATION.md"
    ],
    "package.json": ["docs/guides/DEVELOPMENT.md"],
    "pyproject.toml": ["docs/guides/DEVELOPMENT.md"],
}
```

## Check Changed Files

```bash
# Get list of changed files
git diff --name-only HEAD~1

# Or for uncommitted changes
git diff --name-only

# Or for staged changes
git diff --cached --name-only
```

## Documentation Update Checklist

When updating docs:

1. **Keep examples current** - Code examples should match actual implementation
2. **Update version numbers** if applicable
3. **Add new sections** for new features
4. **Remove deprecated info** for removed features
5. **Check cross-references** - Ensure links still work

## Quick Doc Lookup Commands

```bash
# Find docs mentioning a topic
grep -r "hook" docs/ --include="*.md"

# List all doc files
find docs/ -name "*.md"

# Check doc file sizes
wc -l docs/**/*.md
```

## Documentation Structure

```
docs/
├── README.md                    # Doc index
├── ARCHITECTURE.md              # System architecture
├── CHEATSHEET.md               # Quick commands
├── SYSTEM_DOCUMENTATION.md     # Complete system overview
├── api/
│   └── API_REFERENCE.md        # API endpoints
├── guides/
│   ├── DEVELOPMENT.md          # Dev setup
│   ├── HOOKS_DEVELOPMENT.md    # Creating hooks
│   ├── SYSTEM_GUIDE.md         # Operations
│   └── BATCH_PROCESSING.md     # Batch workflows
└── reference/
    └── LEGACY_FILES_REFERENCE.md  # Legacy code reference
```

## When NOT to Update Docs

- Typo fixes in code
- Internal refactoring (no API change)
- Test additions only
- Dependency updates (unless breaking)
- Code comments only
