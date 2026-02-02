# Claude Code: Complete Configuration Guide (2026)

> A comprehensive, tech-stack-agnostic guide for configuring Claude Code from scratch.
> Compiled from official Anthropic documentation, hackathon-winning configurations, and production-tested community practices.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [File System Layout](#2-file-system-layout)
3. [Step 1: CLAUDE.md — Project Memory](#step-1-claudemd--project-memory)
4. [Step 2: Rules — Modular Guidelines](#step-2-rules--modular-guidelines)
5. [Step 3: Plugins — Packaged Extensions](#step-3-plugins--packaged-extensions)
6. [Step 4: Skills — On-Demand Knowledge](#step-4-skills--on-demand-knowledge)
7. [Step 5: Subagents — Isolated Workers](#step-5-subagents--isolated-workers)
8. [Step 6: Slash Commands — Workflow Shortcuts](#step-6-slash-commands--workflow-shortcuts)
9. [Step 7: Hooks — Deterministic Automation](#step-7-hooks--deterministic-automation)
10. [Step 8: MCP Servers — External Service Connections](#step-8-mcp-servers--external-service-connections)
11. [Step 9: Permissions — Safety Boundaries](#step-9-permissions--safety-boundaries)
12. [Step 10: Context Management Strategy](#step-10-context-management-strategy)
13. [Step 11: Monorepo vs Separate Repos](#step-11-monorepo-vs-separate-repos)
14. [Step 12: Parallel Workflows](#step-12-parallel-workflows)
15. [Step 13: Editor Integration](#step-13-editor-integration)
16. [Step 14: Vercel Integration — Skills, MCP & Deployment](#step-14-vercel-integration--skills-mcp--deployment)
17. [Step 15: CI/CD Integration](#step-15-cicd-integration)
18. [Keyboard Shortcuts Reference](#keyboard-shortcuts-reference)
19. [Useful Built-in Commands Reference](#useful-built-in-commands-reference)
20. [Troubleshooting](#troubleshooting)
21. [Sources](#sources)

---

## 1. Architecture Overview

Claude Code has 8 extension layers that plug into different parts of the agentic loop:

| Layer | What It Does | When It Loads | Context Cost |
|-------|-------------|---------------|--------------|
| **CLAUDE.md** | Persistent project context and instructions | Session start (always) | Every request |
| **Rules** | Modular guidelines, optionally path-scoped | Session start (always) | Every request |
| **Plugins** | Packaged bundles of skills, hooks, agents, and MCP servers | Session start | Varies |
| **Skills** | On-demand knowledge and invocable workflows | Description at start; full content when used | Low until invoked |
| **Subagents** | Isolated workers with separate context windows | When spawned | Zero (isolated) |
| **Commands** | Slash-command shortcuts for common tasks | When invoked | One-time on invoke |
| **Hooks** | Deterministic shell scripts on lifecycle events | On trigger | Zero (external) |
| **MCP Servers** | Connections to external services and tools | Session start | Every request |

**Key principle:** CLAUDE.md and rules are *always-on* context. Skills, subagents, and commands are *on-demand*. Hooks run *outside* the AI loop entirely. Design your setup to minimize always-on context and maximize on-demand loading.

**Recommended setup order:** Install plugins first (Step 3), then check what skills, agents, and hooks they provide before creating custom ones (Steps 4-7). This avoids duplicating functionality that a plugin already covers.

---

## 2. File System Layout

### Global Configuration (all projects)

```
~/.claude/
├── CLAUDE.md                 # Personal global preferences
├── settings.json             # Global hooks, permissions, MCP servers
├── commands/                 # Global slash commands
│   └── my-command.md
├── skills/                   # Global skills
│   └── my-skill/
│       └── SKILL.md
└── agents/                   # Global subagents (if needed)
    └── my-agent.md
```

### Project Configuration

```
your-project/
├── CLAUDE.md                 # Project instructions (committed to git)
├── CLAUDE.local.md           # Personal local overrides (gitignored)
├── .claude/
│   ├── CLAUDE.md             # Alternative location for project instructions
│   ├── settings.json         # Project settings — hooks, permissions (committed)
│   ├── settings.local.json   # Local settings (gitignored)
│   ├── commands/             # Project slash commands
│   │   └── my-command.md
│   ├── agents/               # Subagent definitions
│   │   └── my-agent.md
│   └── skills/               # Project skills
│       └── my-skill/
│           ├── SKILL.md
│           └── supporting-files...
```

### Monorepo Structure (hierarchical CLAUDE.md)

```
monorepo/
├── CLAUDE.md                 # Root: shared rules (always loaded)
├── .claude/                  # Shared config
├── apps/
│   ├── frontend/
│   │   └── CLAUDE.md         # Frontend-only rules (auto-loads in this dir)
│   └── backend/
│       └── CLAUDE.md         # Backend-only rules (auto-loads in this dir)
└── packages/
    └── shared/
        └── CLAUDE.md         # Shared package rules (auto-loads in this dir)
```

**How loading works:** Claude reads CLAUDE.md files from the working directory up to the root. Child directory files (e.g., `apps/frontend/CLAUDE.md`) load automatically when Claude accesses files in that directory. This means backend rules never pollute frontend context and vice versa.

### Loading Priority (highest to lowest)

| Level | Location | Purpose |
|-------|----------|---------|
| Managed policy | `/etc/claude-code/CLAUDE.md` (Linux) | Org-wide (admin) |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared (committed) |
| Project rules | `./.claude/rules/*.md` | Modular topic rules (committed) |
| Project local | `./CLAUDE.local.md` | Personal project overrides (gitignored) |
| User global | `~/.claude/CLAUDE.md` | Personal defaults (all projects) |

All levels are loaded and merged. When instructions conflict, more specific levels take precedence.

---

## Step 1: CLAUDE.md — Project Memory

CLAUDE.md is loaded into every request. It defines what Claude always knows about your project.

### Guidelines

- **Keep it under 500 lines** — bloated CLAUDE.md files cause Claude to ignore instructions.
- For each line, ask: *"Would removing this cause Claude to make mistakes?"* If not, cut it.
- Move reference material to skills (on-demand loading).
- Use imperative language: "Use X" and "Never do Y" — not "It would be nice if..."
- State what NOT to do — prohibitions are more valuable than suggestions.

### Template: Root CLAUDE.md

```markdown
# Project: [PROJECT NAME]

[One-line description of the project and its purpose.]

## Tech Stack

- [Language/Framework]: [version]
- [Database]: [type]
- [Testing]: [framework]
- [Package Manager]: [name]
- [Other key tools]

## Project Structure

[directory tree showing key folders and their purposes]

## Commands

- `[command]` — [what it does]
- `[command]` — [what it does]
- `[command]` — [what it does]
- `[test command]` — [run specific test file]
- `[lint command]` — [run linter]
- `[typecheck command]` — [run type checker]
- `[db command]` — [database operations]

## Code Conventions

- [Rule about types/typing]
- [Rule about naming]
- [Rule about file organization]
- [Rule about imports]
- [Rule about error handling pattern]
- [Rule about exports (named vs default)]

## Architecture Rules

- [Key architectural pattern (e.g., layered, hexagonal)]
- [Data flow direction (e.g., routes → services → repositories)]
- [State management approach]
- [API response format]

## Testing Rules

- [Test framework and patterns]
- [Where tests live]
- [What to mock, what not to mock]
- [Coverage requirements]
- IMPORTANT: Run specific test file during dev, not full suite

## Git Conventions

- [Commit format (e.g., conventional commits)]
- [Branch naming]
- Never commit [secrets, env files, etc.]
- Never force-push to [protected branches]

## Security

- Never hardcode secrets — use environment variables
- Validate all user input server-side
- Never expose internal error details to client
- Never log PII or tokens
```

### Template: Global ~/.claude/CLAUDE.md

```markdown
# Personal Preferences

## Communication
- Be direct and concise
- Don't repeat back what I said
- If unsure, ask rather than guess
- Only add comments for "why", never for "what"

## Code Style
- Prefer early returns over deep nesting
- [Indentation preference]
- [Max line length]
- Don't add unnecessary type annotations to obvious types
- Don't add docstrings/comments to code you didn't change

## Safety
- Never run destructive commands without asking
- Never modify .env files without approval
- Never push to main/master directly
- Show diffs before committing
```

### Template: CLAUDE.local.md (gitignored, personal)

```markdown
# Local Development Notes

## My Environment
- Database on localhost:[port]
- [Service] on localhost:[port]
- Working on branch: [feature-branch]

## Personal Reminders
- [Module X] is being refactored — check with [person] before changing
- Staging URL: [url]
```

### Import Syntax

CLAUDE.md files can reference other files:

```markdown
See @README.md for project overview.
See @docs/api-spec.md for API documentation.
See @package.json for available commands.
```

---

## Step 2: Rules — Modular Guidelines

Rules are markdown files in `.claude/rules/` that organize guidelines by topic. They are always loaded (like CLAUDE.md) but can be **scoped to specific file paths** using YAML frontmatter.

### When to Use Rules vs CLAUDE.md

| Use CLAUDE.md for | Use Rules for |
|-------------------|---------------|
| Project overview, tech stack | Topic-specific guidelines |
| Key commands | Path-scoped conventions |
| Architecture summary | Detailed patterns per domain |
| Always-needed context | Team-agreed standards |

### Path-Scoped Rules

Rules can target specific directories using `paths` frontmatter:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/routes/**/*.ts"
---

# API Development Rules

- All endpoints must validate input with schema validation
- Use consistent response format: { data, error, meta }
- Return proper HTTP status codes
```

This rule only loads when Claude is working on files matching those paths.

### Recommended Rule Files

#### `.claude/rules/coding-style.md`

```markdown
# Coding Style

- [Language-specific style rules]
- Prefer immutability — use const/readonly/final where possible
- Early returns over nested conditionals
- Max function length: [N] lines — split if larger
- Max file length: [N] lines — split if larger
- Functions do one thing — if the name has "and", split it
- No magic numbers — use named constants
- Group imports: stdlib → external → internal → types
- Named exports over default exports (easier to refactor/search)
```

#### `.claude/rules/testing.md`

```markdown
# Testing Rules

- Test behavior, not implementation details
- Arrange-Act-Assert pattern for all tests
- Descriptive names: "should [expected] when [condition]"
- One logical assertion per test (related assertions are fine)
- Mock at boundaries (network, database, filesystem) not internal modules
- Never test private/internal functions directly
- Use factories/fixtures for test data — not inline literals
- Colocate tests with source: `foo.ts` → `foo.test.ts`
- Integration tests > unit tests for API endpoints
- Every new feature/endpoint needs at least one test
- IMPORTANT: Run the specific test file, not the full suite
```

#### `.claude/rules/security.md`

```markdown
# Security Rules

- Never log sensitive data (passwords, tokens, PII)
- Always validate and sanitize user input on the server
- Use parameterized queries — never string concatenation for SQL
- Store secrets in environment variables, never in code
- Never commit .env, credentials, or API keys
- Hash passwords with modern algorithms (argon2/bcrypt) — never MD5/SHA
- Set security headers (CSP, X-Frame-Options, HSTS)
- Rate limit all public endpoints
- CORS: whitelist specific origins, never wildcard in production
- File uploads: validate MIME type, limit size, use allowlist for extensions
- Never expose stack traces or internal error details to clients
```

#### `.claude/rules/git-workflow.md`

```markdown
# Git Workflow

- Conventional commits: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, perf, test, chore, ci
  - Scope: module or area affected
- Imperative mood: "add feature" not "added feature"
- Keep commits atomic — one logical change per commit
- Never commit commented-out code
- Never force-push to main/master
- Feature branches for all changes
- Squash WIP commits before merge
```

#### `.claude/rules/performance.md`

```markdown
# Performance Guidelines

- Use subagents (haiku model) for exploration and simple searches
- Use sonnet for standard implementation tasks
- Use opus for complex architecture decisions and security reviews
- Profile before optimizing — don't guess bottlenecks
- Prefer lazy loading for optional dependencies
- Add indexes for columns used in WHERE, ORDER BY, and JOIN clauses
- Use pagination for all list endpoints
- Cache expensive computations — invalidate on mutation
```

#### `.claude/rules/agent-delegation.md`

```markdown
# Agent Delegation Rules

When to delegate to subagents:
- Security review: ALWAYS delegate security-sensitive changes to the security-reviewer agent
- Code review: Delegate completed features to code-reviewer before PR
- Build errors: Delegate compilation failures to build-fixer agent
- Test writing: Delegate comprehensive test creation to test-writer agent
- Database changes: Delegate schema reviews to database-reviewer agent
- Planning: Use planner agent for features touching 3+ files

When NOT to delegate:
- Simple single-file edits
- Typo fixes
- Adding a single test
- Configuration changes
```

---

## Step 3: Plugins — Packaged Extensions

Plugins bundle skills, hooks, agents, and MCP servers into installable packages. **Install plugins before creating custom skills, agents, or hooks** — plugins often provide these features out of the box, and installing them first lets you identify gaps to fill with custom configuration rather than duplicating existing functionality.

### Installation

Plugins are installed interactively inside a Claude Code session using `/plugin` commands. They **cannot** be installed via Bash or external scripts — you must run these commands in the Claude Code terminal.

```
/plugin marketplace add <marketplace-repo>     # Add a marketplace source
/plugin install <plugin-name>                   # Install from marketplace
/plugins                                        # List installed plugins
/plugin remove <plugin-name>                    # Remove a plugin
```

### What Plugins Can Provide

A single plugin may bundle multiple extension types:

| Extension | Example |
|-----------|---------|
| **Skills** | TDD workflow, debugging methodology, design patterns |
| **Agents** | Code reviewer, security auditor, test writer |
| **Hooks** | Auto-format, branch protection, lint-on-save |
| **MCP Servers** | Database connections, service integrations |
| **Commands** | Custom slash commands |

After installing a plugin, check what it provides by running `/plugins` and reviewing the loaded skills/agents. This prevents creating duplicates in later steps.

### Essential Plugins

#### 1. Language Server (MUST HAVE)

Gives Claude real-time type errors, go-to-definition, and find-references — dramatically improves code quality.

```
/plugin marketplace add boostvolt/claude-code-lsps

# Install for your language:
/plugin install vtsls@claude-code-lsps          # TypeScript/JavaScript
/plugin install pyright@claude-code-lsps        # Python
/plugin install rust-analyzer@claude-code-lsps  # Rust
/plugin install gopls@claude-code-lsps          # Go
```

**Important:** The `typescript-lsp` plugin from the official marketplace is broken (empty README, no tools). Use `vtsls` from `boostvolt/claude-code-lsps` instead — it works correctly and provides full TypeScript language server integration.

#### 2. Superpowers (Recommended)

20+ production-proven skills including TDD, systematic debugging, root cause tracing, structured planning, and workflow management.

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers
```

This plugin provides skills that overlap with many common custom configurations. Check its skill list before creating custom TDD, debugging, or planning skills.

#### 3. Service-Specific Plugins

Install plugins for services your project uses. These often provide MCP server connections that would otherwise require manual configuration:

```
# Supabase — provides Supabase MCP (database, auth, storage)
/plugin marketplace add supabase/supabase-plugin
/plugin install supabase

# Stripe — provides Stripe MCP (payments, webhooks)
/plugin install stripe
```

**Important:** Service plugins often include MCP servers. After installing a service plugin, check if it already provides the MCP connection before adding a separate MCP server in Step 8. For example, the Supabase plugin provides a Supabase MCP server — adding another one manually would be redundant.

#### 4. Commit Commands (Optional)

Automated conventional commits and PR creation.

```
/plugin install commit-commands
```

#### 5. PR Review Toolkit (Optional)

Multi-agent code reviews with confidence scoring.

```
/plugin install pr-review-toolkit
```

#### 6. Everything Claude Code (Optional — all-in-one)

The hackathon-winning configuration as a plugin. Includes all agents, skills, commands, and hooks.

```
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
```

**Warning:** This plugin is comprehensive but may conflict with custom configuration you create in later steps. Best used as a starting point for new projects that don't need fine-tuned control.

### Plugin Budget

**Keep only 4-5 plugins active** — each consumes context window. Plugins load their skill descriptions and tool definitions at session start. You can check context impact with `/context`.

### Post-Installation Checklist

After installing plugins, before proceeding to Steps 4-7:

1. Run `/plugins` to see all installed plugins and what they provide
2. Note which skills are already covered (TDD, debugging, review, etc.)
3. Note which MCP servers are already connected (Supabase, Stripe, etc.)
4. Note which agents are already available
5. Only create custom skills/agents/commands/hooks for gaps not covered by plugins

### Enabled Plugins Configuration

Plugins are tracked in `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "vtsls@claude-code-lsps": true,
    "superpowers@claude-plugins-official": true,
    "supabase@claude-plugins-official": true
  }
}
```

---

## Step 4: Skills — On-Demand Knowledge

Skills are the most flexible extension. They load descriptions at session start (low cost) and full content only when invoked or auto-matched.

**Before creating skills**, check what your installed plugins (Step 3) already provide. Many plugins include skills for common workflows like TDD, debugging, and code review.

### Skill File Structure

```
.claude/skills/
└── my-skill/
    ├── SKILL.md           # Main skill file (required)
    ├── PATTERNS.md        # Supporting reference (optional)
    ├── EXAMPLES.md        # Examples (optional)
    └── scripts/           # Supporting scripts (optional)
        └── validate.sh
```

### SKILL.md Format

```yaml
---
name: skill-name
description: |
  One-paragraph description of when this skill should be used.
  Claude matches tasks to this description to decide relevance.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
# disable-model-invocation: true    # Uncomment to hide from Claude (manual-only)
# context: fork                     # Uncomment to run in isolated subagent context
---

# Skill Title

[Instructions for Claude when this skill activates]

## When to Use
[Conditions that trigger this skill]

## Process
1. [Step one]
2. [Step two]
3. [Step three]

## Patterns
[Code patterns, conventions, templates]

## Anti-Patterns
[What NOT to do]
```

### Essential Skills to Create

#### Verification Loop (pre-PR quality gate)

```yaml
---
name: verification-loop
description: |
  Structured 6-phase verification for code changes. Use before creating
  PRs or after completing features. Runs build, typecheck, lint, tests,
  security scan, and diff review.
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

# Verification Loop

Run this 6-phase check before any PR or after major changes.

## Phase 1: Build
Run the project build command. Stop if it fails.

## Phase 2: Type Check
Run the type checker. Report all errors with file paths and line numbers.

## Phase 3: Lint
Run the linter across all modified files. Report violations.

## Phase 4: Test Suite
Run the test suite with coverage. Target: 80%+ coverage on changed files.
Report failing tests with full error output.

## Phase 5: Security Scan
Scan for:
- Hardcoded secrets, API keys, passwords
- Leftover console.log / print / debug statements
- TODO/FIXME/HACK comments in new code
- Exposed internal error messages

## Phase 6: Diff Review
Run `git diff` and check for:
- Unintended file changes
- Large files that shouldn't be committed
- Merge conflict markers
- Files that belong in .gitignore

## Report Format

Produce a verification report:
| Phase | Status | Details |
|-------|--------|---------|
| Build | PASS/FAIL | [errors if any] |
| Types | PASS/FAIL | [error count] |
| Lint  | PASS/FAIL | [violation count] |
| Tests | PASS/FAIL | [pass/fail count, coverage %] |
| Security | PASS/FAIL | [findings] |
| Diff  | PASS/FAIL | [issues] |

**Overall: READY / NOT READY for PR**

## Continuous Use
During long sessions, run every 15 minutes or after completing a function/component.
```

#### Strategic Compact (context management)

```yaml
---
name: strategic-compact
description: |
  Context management through intentional compaction at logical workflow
  boundaries. Suggests /compact at the right moments.
allowed-tools: Read, Bash
disable-model-invocation: true
---

# Strategic Compact

## When to Compact
- After exploration/planning, before implementation
- After completing a milestone (feature, module, refactor)
- After a debugging session
- After reviewing many files
- When context percentage exceeds 60%

## When NOT to Compact
- During active implementation (you'll lose working context)
- While debugging (you'll lose the error trail)
- Mid-conversation about a specific problem

## How to Compact
Run `/compact` with a summary prompt:

```
/compact Retain: [what to keep]. Completed: [what's done]. Next: [what's next].
```

This preserves the important context while freeing space.
```

### Skills vs Other Features

| If you need... | Use... |
|----------------|--------|
| "Always do X" rules | CLAUDE.md |
| Topic-specific guidelines | `.claude/rules/` |
| Reference material Claude needs sometimes | Skill |
| Workflow triggered with `/<name>` | Skill (or Command) |
| Isolated worker with limited tools | Subagent |
| External service connection | MCP Server |
| Deterministic automation | Hook |
| Bundled set of skills + agents + hooks | Plugin |

### skills.sh — The Open Skills Marketplace

[skills.sh](https://skills.sh/) is the open agent skills directory launched by Vercel in January 2026. It provides a centralized marketplace for discovering, installing, and sharing reusable AI agent skills across 14+ platforms (Claude Code, Cursor, Windsurf, Cline, GitHub Copilot, and others).

Skills from skills.sh follow the Agent Skills Standard and install into `.agents/skills/` (not `.claude/skills/`). Claude Code discovers them automatically alongside project-level skills.

#### Installation

```bash
# Install all skills from a repository
npx skills add <owner/repo>

# Install a specific skill from a multi-skill repository
npx skills add "<owner/repo>" --skill "<skill-name>" --yes

# Examples
npx skills add vercel-labs/agent-skills                             # All Vercel skills
npx skills add "affaan-m/everything-claude-code" --skill "strategic-compact" --yes  # Specific skill
```

**Important syntax notes:**
- To install a **specific skill** from a repository that contains multiple skills, use the `--skill` flag: `npx skills add "<owner/repo>" --skill "<skill-name>" --yes`
- Do **not** use the `@skill-name` suffix (e.g., `npx skills add owner/repo@skill-name`) — this is interpreted as a git tag/version, not a skill name, and will fail with an authentication error
- The `--yes` flag skips confirmation prompts for non-interactive installation
- Quote the repository path if it contains special characters

After installing, restart Claude Code. Skills appear in `/skills` and activate automatically when Claude matches a task to the skill's description.

#### What's Available

skills.sh organizes skills by category with a leaderboard ranked by installs:

| Category | Examples |
|----------|---------|
| **React & Web** | React best practices (45 rules), web design guidelines, component patterns |
| **Backend** | Architecture patterns, database optimization, API design |
| **Testing & CI/CD** | TDD workflows, test generation, deployment automation |
| **Design & UI/UX** | Design system documentation, accessibility audits, Figma-to-code |
| **Language-Specific** | TypeScript patterns, Python conventions, Go idioms |
| **DevOps** | Docker, Kubernetes, infrastructure as code |
| **Documentation** | Technical writing, README updaters, changelog management |

#### skills.sh vs Manual Skills

| Aspect | skills.sh | Manual `.claude/skills/` |
|--------|-----------|--------------------------|
| **Install** | `npx skills add <repo>` — packaged, versioned | Write files yourself |
| **Install location** | `.agents/skills/` | `.claude/skills/` |
| **Updates** | Re-run installer, versioned via git tags | Manual maintenance |
| **Sharing** | Public marketplace with leaderboard | Local or team-only |
| **Portability** | Works across 14+ AI platforms (Agent Skills Standard) | Claude Code only |
| **Advanced features** | Basic SKILL.md format | Full Claude Code features: `context: fork`, `allowed-tools`, model override, hooks |
| **Best for** | General-purpose, well-maintained community knowledge | Project-specific workflows, proprietary patterns |

#### Agent Skills Standard (agentskills.io)

skills.sh is built on the **Agent Skills Standard** — an open specification that makes skills portable across different AI coding tools. A skill written for Claude Code also works in Cursor, Windsurf, and other compatible agents. This standard defines the SKILL.md format, metadata fields, and discovery mechanism.

#### Recommended Approach: Hybrid

The 2026 best practice is to combine plugins, marketplace skills, and custom skills:

1. **Install plugins first** (Step 3) for bundled functionality:
   ```
   /plugin install vtsls@claude-code-lsps         # Language server
   /plugin install superpowers                      # 20+ workflow skills
   ```

2. **Install from skills.sh** for general-purpose, well-maintained skills not covered by plugins:
   ```bash
   npx skills add vercel-labs/agent-skills          # React/Next.js optimization
   npx skills add "affaan-m/everything-claude-code" --skill "verification-before-completion" --yes
   ```

3. **Create manually** for project-specific workflows:
   - Verification loops tailored to your build/test pipeline
   - Domain-specific knowledge (your API patterns, database conventions)
   - Workflows needing Claude Code advanced features (`context: fork`, tool restrictions)

This gives you plugin-managed tooling, community-maintained quality for general patterns, and full control over project-specific workflows.

#### Creating Skills for skills.sh

To contribute a skill to the marketplace:

1. Create a public GitHub repository with your skill
2. Follow the SKILL.md format with clear `name` and `description` frontmatter
3. Submit to skills.sh for listing
4. Skills are ranked by anonymous install telemetry

**Tips for discoverability:**
- Write keyword-rich descriptions — Claude uses these to decide when to load the skill
- Keep SKILL.md under 500 lines — split large content into reference files
- Include input/output examples, not just descriptions
- Test across models (Haiku, Sonnet, Opus) for reliability

#### Context Efficiency

skills.sh skills follow the same context rules as manual skills:
- **Startup cost**: Only skill name + description loaded (~100 tokens per skill)
- **On-demand**: Full SKILL.md content loaded only when Claude decides to use it
- **Reference files**: Supporting files (PATTERNS.md, EXAMPLES.md) loaded only when needed
- **No penalty for unused skills**: Large skill libraries don't consume tokens until accessed

---

## Step 5: Subagents — Isolated Workers

Subagents run in their own context window with limited tools. They explore, analyze, or work independently and return a summary — keeping your main context clean.

### Subagent File Format

Place in `.claude/agents/`:

```yaml
---
name: agent-name
description: |
  When to use this agent. Claude matches tasks to this description.
  Be specific so Claude delegates correctly.
model: sonnet          # or: opus, haiku, inherit
tools: Read, Grep, Glob, Bash, Write, Edit    # limit to what's needed
# skills:             # optional: preload skills into subagent context
#   - skill-name
---

[System prompt for the subagent]

## Your Role
[What this agent does]

## Process
1. [Step]
2. [Step]

## Output Format
[How to structure the response]
```

### Recommended Subagents

**Before creating these**, check if your installed plugins (Step 3) already provide equivalent agents. For example, the `superpowers` plugin includes planning and debugging agents.

#### Planner

```yaml
---
name: planner
description: |
  Expert planning specialist. Use when implementing features that touch
  3+ files, require architecture decisions, or need refactoring strategy.
  Decomposes complex requirements into actionable steps.
model: opus
tools: Read, Grep, Glob
---

You are an expert planning specialist. Decompose complex requirements into
actionable implementation steps.

## Process
1. Analyze requirements thoroughly
2. Review existing codebase architecture
3. Identify all affected files and dependencies
4. Sequence implementation for incremental testing
5. Flag risks and edge cases

## Output
Produce a numbered plan with:
- Exact file paths for each change
- What to add/modify/remove
- Order of implementation
- Verification steps between phases
- Risks and mitigations

## Quality Standards
- Be specific: exact file paths and function names
- Minimize changes — don't refactor beyond scope
- Maintain existing patterns
- Consider error cases and edge conditions
- Plans should enable incremental testing

## Red Flags to Watch For
- Functions exceeding 50 lines
- Deep nesting (3+ levels)
- Code duplication across files
- Missing error handling on I/O operations
```

#### Code Reviewer

```yaml
---
name: code-reviewer
description: |
  Senior code review specialist. Use after completing features or before
  PRs. Reviews for quality, security, performance, and best practices.
model: sonnet
tools: Read, Grep, Glob, Bash
---

You are a senior code reviewer. Review changes against a comprehensive checklist.

## Process
1. Run `git diff` to see all changes
2. Read each modified file in full
3. Check against all categories below
4. Produce structured report

## Review Categories

### Security (Critical)
- Hardcoded credentials or secrets
- SQL/NoSQL injection vulnerabilities
- XSS risks (unescaped user input in output)
- Missing input validation
- Path traversal vulnerabilities
- Authentication/authorization bypasses
- CSRF vulnerabilities

### Code Quality (High)
- Functions longer than 50 lines
- Files longer than 300 lines
- Nesting deeper than 3 levels
- Missing error handling
- Leftover debug statements (console.log, print, etc.)
- Unintended mutations
- Missing test coverage for new code

### Performance (Medium)
- N+1 query patterns
- Missing database indexes for new queries
- Unnecessary re-renders / recomputations
- Unbounded list operations (missing pagination)
- Synchronous operations that should be async
- Missing memoization for expensive computations

### Best Practices (Medium)
- Unclear naming (variables, functions, files)
- Missing documentation for complex logic
- Inconsistent patterns vs existing codebase
- Magic numbers without named constants
- Dead code or unused imports

## Verdict
- **Approve**: No critical or high issues
- **Warning**: Medium issues only — mergeable with notes
- **Block**: Critical or high issues — must fix
```

#### Security Reviewer

```yaml
---
name: security-reviewer
description: |
  Security-focused code reviewer. Use when implementing auth, handling user
  input, modifying API endpoints, or touching sensitive data flows.
model: sonnet
tools: Read, Grep, Glob
---

You are a senior security engineer. Review code exclusively for security
vulnerabilities.

## Focus Areas
- Injection (SQL, NoSQL, command, LDAP, XSS)
- Authentication and authorization flaws
- Secrets or credentials in code or logs
- Insecure data handling (PII exposure, weak hashing)
- Missing input validation at boundaries
- Improper error handling that leaks information
- Insecure deserialization
- Missing rate limiting on sensitive endpoints
- CORS misconfiguration
- Missing security headers
- Insecure file upload handling

## Output
For each finding:
- **Severity**: Critical / High / Medium / Low
- **File**: exact path and line number
- **Issue**: what's wrong
- **Impact**: what could go wrong
- **Fix**: concrete code suggestion
```

#### Build Error Resolver

```yaml
---
name: build-fixer
description: |
  Fix build failures, compilation errors, type errors, and lint violations.
  Use when the build breaks and needs systematic fixing.
model: haiku
tools: Read, Grep, Glob, Edit, Bash
---

You fix build errors efficiently.

## Process
1. Run the failing build/typecheck/lint command
2. Capture and parse all error output
3. Read the relevant source files
4. Fix the root cause (not symptoms)
5. Re-run to verify the fix
6. If new errors appear, fix those too (max 3 iterations)

## Rules
- Fix root causes, not symptoms
- Never suppress errors with @ts-ignore, type assertions, or // eslint-disable
  unless absolutely no other option
- Never change public API signatures unless the error requires it
- Preserve existing behavior while fixing types/builds
```

#### Test Writer

```yaml
---
name: test-writer
description: |
  Write comprehensive tests for new or modified code. Use when features
  need test coverage.
model: sonnet
tools: Read, Grep, Glob, Write, Edit, Bash
---

You are a test engineering specialist.

## Process
1. Read the implementation file
2. Identify all code paths, edge cases, error conditions
3. Check existing tests for patterns and frameworks used
4. Write tests following existing conventions
5. Run tests to verify they pass

## Test Structure
- Arrange-Act-Assert pattern
- Descriptive names: "should [expected] when [condition]"
- Group related tests in describe blocks
- One logical assertion per test

## Coverage Targets
- Happy path: all public functions
- Error cases: invalid input, missing data, auth failures
- Edge cases: empty, null, boundary values, concurrent access
- Integration: real database/API calls where existing tests do this

## Rules
- Match the existing test framework and patterns in the project
- Mock at boundaries only (network, database, filesystem)
- Never mock internal modules
- Tests must be independent — no shared mutable state
- Clean up side effects in afterEach/afterAll
```

#### Database Reviewer

```yaml
---
name: database-reviewer
description: |
  Review database schema changes, migrations, queries, and ORM usage.
  Use when modifying database schemas, writing migrations, or adding queries.
model: sonnet
tools: Read, Grep, Glob
---

You are a database specialist. Review database-related changes.

## Check For
- Missing indexes on foreign keys, WHERE columns, ORDER BY columns
- Missing NOT NULL constraints where appropriate
- Missing UNIQUE constraints for business rules
- N+1 query patterns
- Missing transactions for multi-step writes
- Unsafe migration operations (data loss risk)
- Missing rollback logic in migrations
- Schema changes that break existing data
- Missing created_at/updated_at timestamps
- Raw SQL where the ORM could be used

## Migration Safety
- Never modify existing migrations — create new ones
- All new columns must have defaults or be nullable
- Test migration rollback before committing
- Large table alterations may need batching

## Output
For each finding:
- **Severity**: Critical / High / Medium
- **Location**: file path and line
- **Issue**: what's wrong
- **Fix**: concrete suggestion
```

---

## Step 6: Slash Commands — Workflow Shortcuts

Commands are thin entry points — save prompts you'd otherwise type repeatedly. They live in `.claude/commands/` as markdown files.

### Command File Format

```yaml
---
description: Brief description shown in command picker
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
# disable-model-invocation: true   # Only manual invocation
---

[Instructions for Claude when this command is invoked]

$ARGUMENTS — this variable contains whatever the user types after the command
```

### Recommended Commands

#### `/create-endpoint`

```yaml
---
description: Scaffold a new API endpoint with validation, service, repository, and tests
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Create a new API endpoint for: $ARGUMENTS

1. Look at existing endpoints in the project to understand patterns
2. Create the route handler
3. Create the service layer logic
4. Create the data access layer
5. Add input validation schema
6. Register the route
7. Write integration tests
8. Run the tests to verify
9. Run the type checker to verify
```

#### `/create-component`

```yaml
---
description: Scaffold a new UI component with tests
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Create a new UI component for: $ARGUMENTS

1. Look at existing components for patterns, naming, and structure
2. Create the component file with proper types
3. Create the test file following existing test patterns
4. Export from the barrel file if one exists
5. Run the tests to verify
```

#### `/tdd`

```yaml
---
description: Implement a feature using test-driven development
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Implement using TDD: $ARGUMENTS

Process:
1. Write a failing test first
2. Run it — confirm it fails for the right reason
3. Write the minimal code to make it pass
4. Run it — confirm it passes
5. Refactor if needed (keep tests green)
6. Repeat for the next behavior
7. Run full test suite at the end
```

#### `/verify`

```yaml
---
description: Run the full verification loop (build, types, lint, test, security, diff)
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

Run the verification loop skill. Execute all 6 phases and produce the report.
```

#### `/code-review`

```yaml
---
description: Review current changes for quality, security, and best practices
allowed-tools: Read, Grep, Glob, Bash
---

Review all current uncommitted changes:

1. Run `git diff` to see all changes
2. Review each changed file against the code review checklist
3. Check for security issues, code quality, performance, and best practices
4. Produce a structured report with severity levels
5. Give a verdict: Approve / Warning / Block
```

#### `/plan`

```yaml
---
description: Create a detailed implementation plan before coding
allowed-tools: Read, Grep, Glob
---

Create a detailed implementation plan for: $ARGUMENTS

1. Analyze the requirement
2. Explore the codebase to understand current architecture
3. Identify all files that need to change
4. List dependencies and risks
5. Produce a numbered step-by-step plan with exact file paths
6. Include verification steps between phases
7. Do NOT implement — only plan
```

#### `/refactor-clean`

```yaml
---
description: Remove dead code, unused imports, and clean up
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Clean up the codebase:

1. Find and remove unused imports across all files
2. Find and remove dead code (unreachable, unused exports)
3. Remove leftover console.log/print/debug statements
4. Remove commented-out code blocks
5. Fix inconsistent formatting
6. Run the type checker and linter after changes
7. Run tests to verify nothing broke
```

#### `/build-fix`

```yaml
---
description: Fix all build, type, and lint errors
allowed-tools: Read, Edit, Grep, Glob, Bash
---

Fix all build errors:

1. Run the build command and capture errors
2. Run the type checker and capture errors
3. Run the linter and capture errors
4. Fix all errors starting with the most fundamental (types first)
5. Re-run after each fix to check for cascading issues
6. Repeat until clean build (max 5 iterations)
7. Run tests to ensure no regressions
```

#### `/new-feature`

```yaml
---
description: Create a feature branch and prepare for implementation
allowed-tools: Bash
---

Create a new feature branch for: $ARGUMENTS

1. Check that the working tree is clean — if dirty, stop and warn
2. Fetch latest from remote: `git fetch origin`
3. Checkout the development branch and pull latest changes
4. Create and switch to the feature branch: `git checkout -b feature/<slugified-name>`
   - Slugify the name: lowercase, replace spaces with hyphens, remove special characters
5. Confirm the branch was created and is ready for work
6. Show: current branch name, base commit, and that the tree is clean

Do NOT start implementing anything — just set up the branch.
```

#### `/security-review`

```yaml
---
description: Security-focused review of current changes
allowed-tools: Read, Grep, Glob, Bash
---

Perform a security-focused review of all current changes:

1. Run `git diff` to identify all modified files
2. Check each change for security vulnerabilities (OWASP Top 10)
3. Scan for hardcoded secrets, API keys, or credentials
4. Verify input validation on any new endpoints or form handlers
5. Check authentication and authorization logic
6. Report findings with severity levels and fix suggestions
```

### Wrapper Pattern (Advanced)

For large skill sets, use commands as thin wrappers that invoke skills:

```yaml
---
description: Run TDD workflow
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Load and follow the tdd-workflow skill for: $ARGUMENTS
```

This saves ~64% startup context compared to embedding full instructions in every command.

---

## Step 7: Hooks — Deterministic Automation

Hooks are shell scripts that run at specific lifecycle events. They are NOT AI — they execute deterministically every time. This is what makes them powerful: formatting will always happen, not just when Claude "remembers" to do it.

### Hook Events

| Event | When It Fires | Use Case |
|-------|--------------|----------|
| `PreToolUse` | Before a tool executes | Block dangerous operations, validate |
| `PostToolUse` | After a tool completes | Format code, run type checks |
| `PermissionRequest` | When permission dialog shows | Auto-allow/deny |
| `UserPromptSubmit` | When you press Enter | Inject context, log prompts |
| `Stop` | When Claude finishes responding | Final verification, log summary |
| `SubagentStop` | When a subagent completes | Post-process subagent work |
| `Notification` | When Claude needs attention | Desktop notifications |
| `PreCompact` | Before context compression | Preserve critical state |
| `SessionStart` | Session begins or resumes | Restore context, detect environment |
| `SessionEnd` | Session ends | Save state, extract learnings |
| `Setup` | On `--init` or `--maintenance` | Project initialization |

### Configuration Location

Hooks go in `settings.json` (project or global):

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "shell command here"
          }
        ]
      }
    ]
  }
}
```

- `matcher`: tool name pattern to match (e.g., `"Edit|Write"`, `"Bash"`, `"*"` for all, `""` for no-tool events)
- `command`: shell command to run. Receives tool input as JSON on stdin.
- Exit code 0 = success (hook output suppressed). Exit code 2 = block tool + show output as feedback.

### Environment Variables Available in Hooks

| Variable | Description |
|----------|-------------|
| `$CLAUDE_PROJECT_DIR` | Root directory of the project |

Tool input is passed via **stdin as JSON** with fields like `tool_name`, `tool_input.file_path`, `tool_input.command`, etc.

### Recommended Hook Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read fp; if echo \"$fp\" | grep -qE '\\.(ts|tsx|js|jsx|mjs|css|json|md)$'; then npx prettier --write \"$fp\" 2>/dev/null; fi; } || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path // empty' | { read fp; blocked=false; for pattern in .env package-lock.json pnpm-lock.yaml yarn.lock .git/ node_modules/ dist/ .next/ build/; do case \"$fp\" in *\"$pattern\"*) blocked=true;; esac; done; if $blocked; then echo \"BLOCKED: Writing to $fp is not allowed.\" >&2; exit 2; fi; } || true"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // empty' | { read cmd; branch=$(cd \"$CLAUDE_PROJECT_DIR\" && git rev-parse --abbrev-ref HEAD 2>/dev/null); if echo \"$cmd\" | grep -qE '^git commit' && echo \"$branch\" | grep -qE '^(main|master|dev)$'; then echo \"BLOCKED: Never commit directly on $branch. Create a feature branch first.\" >&2; exit 2; fi; if echo \"$cmd\" | grep -qE 'git push.*(origin )?(main|master|dev)( |$)'; then echo \"BLOCKED: Never push directly to $branch. Merge via PR only.\" >&2; exit 2; fi; } || true"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // empty' | { read cmd; if echo \"$cmd\" | grep -qiE '^git push'; then echo 'REMINDER: Review changes before pushing. Run /verify first.' >&2; fi; } || true"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && git diff --name-only 2>/dev/null | xargs grep -l 'console\\.log\\|console\\.debug' 2>/dev/null | head -10 | { files=$(cat); if [ -n \"$files\" ]; then echo \"WARNING: Debug statements found in modified files:\" >&2; echo \"$files\" >&2; fi; } || true"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Awaiting your input' 2>/dev/null || osascript -e 'display notification \"Awaiting your input\" with title \"Claude Code\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

**What each hook does:**

| Hook | Trigger | Action |
|------|---------|--------|
| PostToolUse (prettier) | After any file edit | Auto-format with Prettier (ts, tsx, js, jsx, mjs, css, json, md) |
| PreToolUse (file protection) | Before any write | Block writes to .env, lockfiles, .git, node_modules, dist, build |
| PreToolUse (branch protection) | Before git commit/push | Block commits on protected branches (main, master, dev) and direct pushes |
| PreToolUse (git push reminder) | Before git push | Remind to review changes and run /verify |
| Stop (console.log scanner) | When Claude finishes | Scan modified files for leftover debug statements |
| Notification | When Claude needs input | Desktop notification (Linux/macOS) |

### Hook Design Best Practices

1. **Always end with `|| true`** — prevents hook failures from blocking normal Claude operation. Only omit this if you want a hook failure to block the tool.

2. **Use exit code 2 to block** — any hook that outputs to stderr and exits with code 2 will block the tool and show the output as feedback to Claude.

3. **Use `jq` for JSON parsing** — tool input arrives as JSON on stdin. Use `jq -r '.tool_input.file_path'` to extract fields.

4. **Keep hooks fast** — hooks run synchronously. Slow hooks (>5 seconds) degrade the user experience. For heavy operations (full type check, test suite), prefer running them as part of skills or commands instead.

5. **Shell over Python** — shell hooks (`jq` + `grep` + `case`) are more portable and start faster than Python hooks. Use Python only for complex logic.

6. **Test hooks manually** — pipe sample JSON into your hook command to verify it works before adding to settings:
   ```bash
   echo '{"tool_input":{"file_path":"src/index.ts"}}' | jq -r '.tool_input.file_path'
   ```

### Formatter Prerequisites

The auto-format hook requires a code formatter to be installed in your project. If using Prettier:

```bash
# Install Prettier as a dev dependency
npm install --save-dev prettier

# Create .prettierrc config
cat > .prettierrc << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
EOF
```

The hook will silently skip formatting if Prettier is not installed (due to `2>/dev/null` and `|| true`).

### Advanced: Session Persistence Hooks

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-save.js\""
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-restore.js\""
          }
        ]
      }
    ]
  }
}
```

### Interactive Hook Setup

Instead of editing JSON manually, use the built-in UI:

```
/hooks
```

This opens an interactive configurator where you select event types, add matchers, and define commands.

---

## Step 8: MCP Servers — External Service Connections

MCP (Model Context Protocol) connects Claude to external services — databases, APIs, deployment platforms.

**Before adding MCP servers**, check if any installed plugins (Step 3) already provide the connection you need. For example, a Supabase plugin typically includes a Supabase MCP server — adding another one manually would be redundant.

### Configuration

MCP servers are added via the CLI:

```bash
# Standard MCP server (stdio transport)
claude mcp add <server-name> -- npx -y @package/server-name

# HTTP transport (for hosted MCP servers)
claude mcp add --transport http <server-name> https://mcp.example.com

# With environment variables
claude mcp add <server-name> -e API_KEY=your-key -- npx -y @package/server-name

# List configured servers
claude mcp list

# Remove a server
claude mcp remove <server-name>
```

MCP configuration is stored in the local Claude settings file, not in `.claude/settings.json`.

### Recommended MCP Servers

#### Tier 1: Start Here (2-3 max)

| Server | Purpose | Install |
|--------|---------|---------|
| **Context7** | Real-time, version-specific documentation (solves knowledge cutoff) | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| **Sequential Thinking** | Structured reasoning chains for complex problems | `claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking` |

Context7 is particularly valuable for projects using rapidly-evolving frameworks (Next.js, React, Tailwind CSS, etc.) where Claude's training data may be outdated.

#### Tier 2: Add When Needed

| Server | Purpose | Install | Notes |
|--------|---------|---------|-------|
| **GitHub** | PR/issue management | `claude mcp add github` | Often unnecessary — Claude has built-in `gh` CLI access |
| **PostgreSQL** | Direct database queries | `claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://..."` | Skip if using an ORM that handles all queries |
| **Fetch** | Read any URL/API docs | `claude mcp add fetch -- npx -y @modelcontextprotocol/server-fetch` | Claude has built-in `WebFetch` tool |
| **Memory** | Persistent cross-session memory | `claude mcp add memory -- npx -y @modelcontextprotocol/server-memory` | CLAUDE.md + rules often sufficient |
| **Playwright** | Browser automation, E2E testing | `claude mcp add playwright -- npx -y @anthropic/mcp-server-playwright` | Check if `agent-browser` skill covers your needs |
| **Sentry** | Error monitoring | Configure with Sentry auth token | |
| **Supabase** | Supabase DB/auth | Configure with project URL + key | Often provided by Supabase plugin instead |

#### Tier 3: Specialized

| Server | Purpose |
|--------|---------|
| **Vercel** | Deploy frontend, manage projects, search docs (see [Step 14](#step-14-vercel-integration--skills-mcp--deployment) for full setup) |
| **Railway** | Deploy backend |
| **Docker** | Container management |
| **Cloudflare** | Workers, DNS, CDN |
| **ClickHouse** | Analytics database |

### Context Budget Rules

**Each active MCP server consumes context window on every request.**

- Context can shrink from 200k to ~70k with too many active MCPs
- Keep 20-30 configured but only **5-10 active per project**
- Stay under **80 active tools** total
- Use `/mcp` command to check token costs per server
- Disable unused servers at the project level:

```json
{
  "disabledMcpServers": ["playwright", "docker", "cloudflare"]
}
```

- Prefer native tools (Glob, Grep, Read, Explore subagent) for tasks under 1000 files — they cost zero context
- Check for overlap with plugins — a service plugin may already provide the MCP connection

---

## Step 9: Permissions — Safety Boundaries

Permissions control what tools Claude can use without asking.

### Configuration

In `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test*)",
      "Bash(npm install*)",
      "Bash(npx prettier *)",
      "Bash(npx tsc *)",
      "Bash(npx vitest *)",
      "Bash(npx jest *)",
      "Bash(npx playwright *)",
      "Bash(npx eslint *)",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git branch*)",
      "Bash(git checkout *)",
      "Bash(git switch *)",
      "Bash(git fetch*)",
      "Bash(git stash*)",
      "Bash(git merge *)",
      "Bash(git rebase *)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Bash(rm -rf /*)",
      "Read(.env*)",
      "Read(*.pem)",
      "Read(*secret*)",
      "Read(*credential*)"
    ]
  }
}
```

### Permission Syntax

| Pattern | Meaning |
|---------|---------|
| `Bash(npm run lint)` | Exact match |
| `Bash(npm run *)` | Prefix wildcard |
| `Bash(git * main)` | Glob pattern |
| `Read(.env*)` | Block reading env files |
| `Edit(src/**)` | Allow editing anywhere in src/ |

**Evaluation order:** Deny (highest) → Ask → Allow (lowest)

This means deny rules always win. Even if `Bash(git *)` is allowed, `Bash(git push --force*)` will still be blocked because deny rules have higher priority.

### Permission Strategy

1. **Allow generously for development tools** — npm, git read operations, formatters, linters, and test runners should all be pre-approved to avoid constant permission prompts
2. **Deny destructive operations** — force push, hard reset, recursive delete of root
3. **Deny secret access** — env files, credentials, PEM files should require explicit approval each time
4. **Add project-specific allows** — if you use pnpm, yarn, turbo, or other tools, add their patterns:

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm *)",
      "Bash(turbo *)",
      "Bash(yarn *)",
      "Bash(pytest *)",
      "Bash(cargo *)",
      "Bash(go test *)"
    ]
  }
}
```

### User-Local vs Project Permissions

- **`.claude/settings.json`** (committed) — project-wide rules shared by all team members
- **`.claude/settings.local.json`** (gitignored) — personal permissions accumulated during sessions

When Claude asks for permission and you approve, the approval goes to `settings.local.json`. Project-level permissions in `settings.json` apply to everyone.

---

## Step 10: Context Management Strategy

Context window is your most precious resource. Manage it actively.

### Budget Awareness

| Feature | Context Cost |
|---------|-------------|
| CLAUDE.md (500 lines) | ~2-5% per request |
| Each MCP server | ~5-15% per request |
| Each active plugin | ~3-10% per request |
| Skill description (loaded) | ~0.1% per request |
| Skill full content (invoked) | ~2-5% one-time |
| Subagent | 0% (isolated) |
| Hook | 0% (external) |

### Context Optimization Rules

1. **Monitor context**: Use `/context` command to see usage breakdown
2. **Compact strategically**: Run `/compact` after planning (before coding), after milestones, after debugging sessions — not mid-implementation
3. **Use subagents for exploration**: They explore in separate context, return only summaries
4. **Disable unused MCPs**: Each inactive server still costs tokens if configured but not disabled
5. **Use skills instead of bloated CLAUDE.md**: Skills load on-demand; CLAUDE.md loads every request
6. **Clear between unrelated tasks**: Use `/clear` to start fresh — context pollution is the most common failure mode
7. **Name sessions**: Use `/rename` so you can resume later without rebuilding context
8. **Set `disable-model-invocation: true`** on skills you only invoke manually — saves description tokens every request

### Compaction Prompt Template

```
/compact Retain: [current task, key decisions made, files being modified].
Completed: [what's done]. Next: [immediate next step].
```

---

## Step 11: Monorepo vs Separate Repos

### Recommendation: Monorepo

| Factor | Monorepo | Separate Repos |
|--------|----------|----------------|
| Claude context | Hierarchical CLAUDE.md — loads only relevant rules | Burns 40-60% tokens on cross-repo duplication |
| Shared code | Single `packages/shared` — direct imports | Must publish npm packages or copy types |
| Build speed | Turborepo caching + parallel | Independent CI, no shared cache |
| Integration | Claude sees both sides of your API | Must manually sync API contracts |
| CLAUDE.md | Auto-loads per directory | Need `--add-dir` workaround |

### Monorepo Hierarchical CLAUDE.md

```
monorepo/
├── CLAUDE.md                 # Shared rules (always loaded, ~200 lines)
├── apps/
│   ├── web/CLAUDE.md         # Frontend rules (~200 lines, loads in web/)
│   └── api/CLAUDE.md         # Backend rules (~200 lines, loads in api/)
└── packages/
    └── shared/CLAUDE.md      # Shared package rules (~100 lines)
```

This achieves ~80% reduction in per-request context compared to a single monolithic file.

### If You Must Use Separate Repos

#### Option A: `--add-dir`

```bash
cd ~/projects/frontend
claude --add-dir ~/projects/backend

# Or mid-session:
/add-dir ~/projects/backend
```

#### Option B: Parent Directory

```bash
mkdir ~/projects/fullstack
cd ~/projects/fullstack
git clone <frontend> web
git clone <backend> api
claude    # launches in parent, sees both
```

#### Cross-Repo CLAUDE.md Template

Add this identical table to BOTH repos' CLAUDE.md:

```markdown
## Repository Ecosystem

| Repository | Type | Purpose | Location |
|------------|------|---------|----------|
| **web** | Frontend | [Framework] App | `~/projects/web/` |
| **api** | Backend | [Framework] API | `~/projects/api/` |

## Cross-Repo Rules
- Shared types defined in [location] — sync when API shapes change
- API base URL: [env variable]

## Git Safety
IMPORTANT: Before ANY git command, verify directory with `pwd`.
Each repo has separate git history.
```

---

## Step 12: Parallel Workflows

### Git Worktrees (Multiple Claude Instances)

Run multiple Claude instances on different branches without conflicts:

```bash
# Create worktrees
git worktree add ../project-feature-a -b feature-a
git worktree add ../project-bugfix bugfix-123

# Run Claude in each
cd ../project-feature-a && claude
cd ../project-bugfix && claude

# Clean up when done
git worktree remove ../project-feature-a
```

### Conversation Forking

Fork the current conversation for parallel task exploration:

```
/fork
```

This creates an independent branch of the conversation. Original continues unaffected.

### tmux for Long Sessions

```bash
# Create named session
tmux new -s claude-dev

# Detach: Ctrl+B, D
# Reattach:
tmux attach -t claude-dev
```

Use tmux for:
- Dev servers that need persistent logs
- Long-running Claude sessions
- Multiple terminals (splits) with different tasks

---

## Step 13: Editor Integration

### Zed (Recommended for Performance)

- Built-in Agent Panel for real-time file tracking
- `Cmd+Shift+R` — command palette for slash commands
- `Ctrl+G` from Claude Code — opens current files in Zed
- Split-screen: terminal with Claude + editor side by side
- Minimal resource consumption with large codebases

### VS Code / Cursor

- Claude Code runs in the integrated terminal
- `\ide` command syncs file opens with the editor
- Extensions available for deeper integration
- Multi-root workspaces for multi-repo setups

### General Setup

Split-screen workflow:
- **Left**: Terminal with Claude Code
- **Right**: Editor showing current files
- Claude edits files → editor auto-reloads → you review in real time

---

## Step 14: Vercel Integration — Skills, MCP & Deployment

Vercel provides an official ecosystem of agent skills, an MCP server, and deployment tools specifically designed for Claude Code. This step covers all three layers.

### 14.1: Vercel Agent Skills

Vercel released `agent-skills` — a package manager for AI coding agents containing 10+ years of React and Next.js optimization knowledge packaged as installable skills.

#### Installation

```bash
npx add-skill vercel-labs/agent-skills
```

This auto-detects Claude Code (checks for `.claude` directory) and installs skills into `~/.claude/skills/` or `.claude/skills/`.

#### Available Skills

| Skill | What It Provides |
|-------|-----------------|
| **react-best-practices** | 45 rules across 8 categories for React/Next.js performance optimization, prioritized by impact level (CRITICAL → LOW) |
| **web-design-guidelines** | 100+ rules covering accessibility, performance, and UX for UI code audits (ARIA labels, focus states, forms, i18n) |
| **react-native-guidelines** | 16 rules in 7 sections for mobile performance, layout, animations, images, state management |
| **composition-patterns** | Techniques to avoid excessive boolean props through compound components, state management, API design |
| **vercel-deploy-claimable** | One-command deployment with auto-detection for 40+ frameworks, returns preview URL and claimable ownership link |

#### React Best Practices — Category Breakdown

The `react-best-practices` skill is the most impactful. It contains rules organized by priority:

| Category | Impact | What It Catches |
|----------|--------|----------------|
| **Eliminate Waterfalls** | CRITICAL | Sequential async calls that should be parallel, blocking data fetches, cascading `useEffect` chains |
| **Bundle Size Optimization** | CRITICAL | Large client bundles, missing tree-shaking, unnecessary client-side imports, heavy dependencies |
| **Server-Side Performance** | HIGH | Missed Server Component opportunities, unnecessary "use client", improper caching, missing streaming |
| **Client-Side Data Fetching** | MEDIUM-HIGH | Redundant fetches, missing deduplication, poor cache invalidation, over-fetching |
| **Re-render Optimization** | MEDIUM | Unnecessary re-renders, missing memoization, prop drilling causing cascading updates |
| **Rendering Performance** | MEDIUM | Heavy computations in render path, missing virtualization for long lists, layout thrashing |
| **JavaScript Performance** | LOW-MEDIUM | Inefficient loops, unnecessary object creation, suboptimal algorithms |
| **Advanced Patterns** | LOW | Missing Suspense boundaries, suboptimal code splitting, underused streaming patterns |

Each rule includes: problem description, blocking/incorrect code example, optimized/correct code example, and specific impact metrics.

#### How Skills Load

After installation, Claude Code discovers skills automatically:
1. Reads skill descriptions at session start (~100 tokens per skill — low cost)
2. Loads full content only when task matches description
3. Rules activate when Claude is writing React/Next.js code, reviewing performance, or optimizing components

#### Manual Invocation

If Claude doesn't auto-activate a skill, you can invoke directly:

```
Load the react-best-practices skill and review my component for performance issues.
```

Or reference it from a slash command:

```yaml
---
description: Review React components for performance using Vercel best practices
---

Load the react-best-practices skill and review: $ARGUMENTS

Focus on CRITICAL and HIGH impact rules first.
Report each violation with file, line, rule name, and fix.
```

### 14.2: Vercel MCP Server (Official)

The official Vercel MCP server (`https://mcp.vercel.com`) connects Claude Code to your Vercel account for deployment management, log analysis, and documentation search.

#### Setup for Claude Code

```bash
# General access (all projects)
claude mcp add --transport http vercel https://mcp.vercel.com

# Project-specific access (recommended — auto-provides team/project context)
claude mcp add --transport http vercel-myproject https://mcp.vercel.com/my-team/my-project
```

After adding, authenticate:

```
/mcp
```

This opens the OAuth flow in your browser. Once authorized, Claude has secure access to your Vercel account.

#### What Vercel MCP Provides

**Public tools (no auth required):**
- Search and navigate Vercel documentation
- Query framework-specific docs (Next.js, SvelteKit, etc.)

**Authenticated tools (after OAuth):**
- List and inspect projects
- View deployment status, URLs, and metadata
- Analyze deployment and build logs
- Search error logs for debugging
- View environment variables (names only, not values)
- Manage project settings

**Current limitation:** The official MCP is **read-only** in its initial release. It cannot trigger deployments or modify settings. For write operations, use the Vercel CLI or the deploy skill.

#### Project-Specific URLs (Recommended)

Use project-specific MCP URLs for better performance:

```
https://mcp.vercel.com/<teamSlug>/<projectSlug>
```

Benefits:
- Tools auto-detect which project you mean (no manual parameter input)
- Fewer errors from missing project/team slugs
- Streamlined workflow

Find your slugs:
- **Dashboard**: Project → Settings → General
- **CLI**: `vercel projects ls`

#### Multiple Project Connections

You can add multiple MCP connections for different projects:

```bash
claude mcp add --transport http vercel-frontend https://mcp.vercel.com/my-team/frontend-app
claude mcp add --transport http vercel-api https://mcp.vercel.com/my-team/api-service
claude mcp add --transport http vercel-docs https://mcp.vercel.com/my-team/docs-site
```

#### Context Budget Note

Each active MCP connection consumes context window tokens. If you have multiple Vercel MCP connections, disable the ones you're not actively using:

```json
{
  "disabledMcpServers": ["vercel-api", "vercel-docs"]
}
```

### 14.3: Community MCP Server (nganiet/mcp-vercel)

If you need **write access** (trigger deployments, manage env vars), use the community MCP server:

```bash
claude mcp add-json "vercel-write" '{"command":"npx","args":["-y","vercel-mcp"]}'
```

This implements Vercel's REST API as MCP tools:
- Trigger deployments
- Manage environment variables
- Create/delete projects
- Manage domains
- Team operations

**Trade-off:** More capabilities but requires a Vercel API token (less secure than OAuth).

### 14.4: v0 MCP Server (UI Generation)

For generating UI components from natural language or design images:

```bash
# Install v0 MCP for component generation
claude mcp add-json "v0" '{"command":"npx","args":["-y","v0-mcp"]}'
```

Capabilities:
- Generate React/Next.js UI components from text descriptions
- Convert design screenshots into working code
- Iteratively refine components through conversation
- Uses Vercel's v0 AI under the hood

### 14.5: Deployment Skill (Claimable Deploys)

The `vercel-deploy-claimable` skill (installed via `npx add-skill vercel-labs/agent-skills`) enables instant deployment without upfront authentication:

**How it works:**
1. Claude builds your project
2. Deploys to a temporary Vercel preview URL
3. Returns two links:
   - **Preview URL**: live site you can visit immediately
   - **Claim URL**: transfer ownership to your Vercel account

**No authentication required** for the deployment itself. You only authenticate when claiming ownership.

**Trigger phrases:**
- "Deploy my app"
- "Deploy this to production"
- "Create a preview deployment"
- "Deploy and give me the link"
- "Push this live"

**Auto-detects 40+ frameworks** from package.json — Next.js, Vite, Remix, Astro, SvelteKit, etc.

### 14.6: Custom Deploy Command

For a more controlled deployment workflow, create a custom slash command:

#### `.claude/commands/deploy.md`

```yaml
---
description: Build, verify, and deploy to Vercel
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

Deploy the project to Vercel: $ARGUMENTS

## Pre-Deploy Verification
1. Run the full build: [build command]
2. Run type checker: [typecheck command]
3. Run linter: [lint command]
4. Run test suite: [test command]
5. If ANY step fails, STOP and report. Do not deploy broken code.

## Deploy
6. Run `vercel --prod` for production or `vercel` for preview
7. Capture the deployment URL

## Post-Deploy
8. Report the deployment URL
9. If Vercel MCP is connected, check deployment logs for errors
10. Report final status: SUCCESS or FAILED with details
```

### 14.7: Security Best Practices

- **Verify the endpoint**: Always confirm you're connecting to `https://mcp.vercel.com` (the official URL)
- **Supported clients only**: Vercel approves MCP clients that meet their security standards
- **Enable human confirmation**: Always review actions before they execute, especially deployments
- **Confused deputy protection**: Vercel MCP requires explicit user consent per client connection
- **Prompt injection awareness**: Review permissions of all connected tools — a malicious tool could instruct Claude to exfiltrate data via MCP
- **Read-only by default**: The official MCP is read-only, preventing accidental production changes

### 14.8: Vercel Network Allowlist (claude.ai only)

If using the deploy skill from claude.ai (not Claude Code CLI), add Vercel domains to the allowlist:

1. Go to `https://claude.ai/admin-settings/capabilities`
2. Add `*.vercel.com` to allowed domains
3. Retry deployment

This is not needed for Claude Code CLI — only the web interface.

### 14.9: Recommended Vercel Setup Summary

| Layer | What to Install | Purpose |
|-------|----------------|---------|
| **Skills** | `npx add-skill vercel-labs/agent-skills` | React/Next.js best practices, design guidelines, deploy capability |
| **Official MCP** | `claude mcp add --transport http vercel https://mcp.vercel.com/team/project` | Read-only project management, logs, docs |
| **Community MCP** | `claude mcp add-json "vercel-write" '{"command":"npx","args":["-y","vercel-mcp"]}'` | Write access: trigger deploys, manage env vars (optional) |
| **v0 MCP** | `claude mcp add-json "v0" '{"command":"npx","args":["-y","v0-mcp"]}'` | UI component generation from text/images (optional) |
| **Deploy command** | `.claude/commands/deploy.md` | Controlled deployment with pre-checks |

**Start with Skills + Official MCP only.** Add community MCP and v0 when needed. Each active MCP consumes context window.

---

## Step 15: CI/CD Integration

### Claude as a Linter

```json
{
  "scripts": {
    "lint:claude": "claude -p 'You are a linter. Look at changes vs main. Report issues: filename:line on one line, description on the next. No other text.'"
  }
}
```

### Claude for PR Review (GitHub Actions)

```yaml
# .github/workflows/claude-review.yml
name: Claude PR Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Review
        run: |
          git diff origin/main...HEAD | claude -p "Review this diff for bugs, security issues, and best practices. Be concise." --output-format text
```

### Pipe Data Through Claude

```bash
# Explain a build error
cat build-error.txt | claude -p 'Explain the root cause concisely' > diagnosis.txt

# Analyze logs
cat access.log | claude -p 'Find anomalies and potential security issues' --output-format json

# Structured output
claude -p "List all API endpoints in this project" --output-format json
```

### Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Text | `--output-format text` | Simple pipe output (default) |
| JSON | `--output-format json` | Structured data for scripts |
| Stream JSON | `--output-format stream-json` | Real-time processing |

---

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl+U` | Delete entire input line |
| `Shift+Enter` | Multiline input |
| `Tab` | Toggle extended thinking display |
| `Ctrl+O` | Toggle verbose mode (see thinking) |
| `Option+T` / `Alt+T` | Toggle thinking on/off |
| `Esc Esc` | Interrupt current response or restore code |
| `Ctrl+G` | Open current files in editor (Zed) |
| `!command` | Run bash command directly |
| `@filepath` | Reference a file |
| `/command` | Run a slash command |

---

## Useful Built-in Commands Reference

| Command | What It Does |
|---------|-------------|
| `/help` | Show available commands |
| `/hooks` | Interactive hook configurator |
| `/mcp` | Show MCP server status and token costs |
| `/plugins` | List installed plugins |
| `/context` | Show context window usage breakdown |
| `/compact` | Manual context compression |
| `/clear` | Clear conversation (start fresh) |
| `/fork` | Fork conversation for parallel work |
| `/rewind` | Return to previous conversation state |
| `/resume` | Resume a previous session |
| `/rename` | Name current session for later resumption |
| `/checkpoints` | File-level rollback points |
| `/statusline` | Customize status bar display |
| `/config` | Edit global configuration |
| `/add-dir` | Add another directory to workspace |
| `/agents` | Manage subagents |
| `/permissions` | Review and modify permissions |

---

## Troubleshooting

### Context Window Filling Up Fast

- Run `/mcp` — check per-server token costs, disable unused servers
- Run `/context` — see what's consuming space
- Move large CLAUDE.md sections into skills (on-demand loading)
- Use subagents for exploration (isolated context)
- Run `/compact` at logical boundaries

### Claude Ignoring CLAUDE.md Instructions

- File is too long (>500 lines) — Claude loses focus. Trim it.
- Instructions conflict with each other — make rules unambiguous
- Instructions are too soft ("consider doing X") — use imperative ("Always do X", "Never do Y")
- Run `/clear` — stale context may override rules

### Hooks Not Firing

- Check event name matches exactly (case-sensitive): `PreToolUse`, `PostToolUse`, `Stop`
- Check `matcher` pattern matches the tool name: `"Edit|Write"`, `"Bash"`, `"*"`
- Check script is executable: `chmod +x script.sh`
- Run `/hooks` to see registered hooks
- Check `settings.json` vs `settings.local.json` — local overrides project

### MCP Server Not Working

- Run `/mcp` to check connection status
- MCP connections can fail silently mid-session
- If a tool disappears, restart the session
- Check that `npx` can find the package: `npx -y @package/name --help`

### Subagents Not Being Used

- Check the `description` field is specific enough for Claude to match tasks
- Add an `agent-delegation.md` rule file telling Claude when to delegate
- Invoke manually to test: "Use the security-reviewer agent to check this code"

### Plugins Not Working

- Plugin installation is interactive — must be done via `/plugin` commands inside Claude Code
- Plugins cannot be installed via Bash or external scripts
- Run `/plugins` to see installed plugins and their status
- If a plugin provides MCP that needs authentication, run `/mcp` to authenticate

### TypeScript LSP Plugin Not Working

- The official `typescript-lsp` plugin is broken — use `vtsls` instead:
  ```
  /plugin marketplace add boostvolt/claude-code-lsps
  /plugin install vtsls@claude-code-lsps
  ```

### skills.sh Installation Failing

- Use `--skill` flag for specific skills: `npx skills add "owner/repo" --skill "skill-name" --yes`
- Do NOT use `@skill-name` suffix — it's interpreted as a git tag and will fail
- Skills install to `.agents/skills/`, not `.claude/skills/`
- Restart Claude Code after installing marketplace skills

### Slow Performance

- Too many MCP servers active — disable unused ones
- Too many plugins — keep 4-5 max
- CLAUDE.md too large — trim to <500 lines
- Use haiku model for simple tasks, sonnet for standard work, opus for complex decisions

---

## Sources

### Official Documentation
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Extend Claude Code (Features Overview)](https://code.claude.com/docs/en/features-overview)
- [CLAUDE.md / Memory](https://code.claude.com/docs/en/memory)
- [Skills](https://code.claude.com/docs/en/skills)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Hooks Reference](https://code.claude.com/docs/en/hooks)
- [MCP](https://code.claude.com/docs/en/mcp)
- [Plugins](https://code.claude.com/docs/en/plugins)
- [Settings](https://code.claude.com/docs/en/settings)

### Community Guides
- [The Claude Code Setup That Won a Hackathon (Dev Genius)](https://blog.devgenius.io/the-claude-code-setup-that-won-a-hackathon-a75a161cd41c)
- [Everything Claude Code — Hackathon Winner's Config (GitHub)](https://github.com/affaan-m/everything-claude-code)
- [The Complete Guide to CLAUDE.md (Builder.io)](https://www.builder.io/blog/claude-md-guide)
- [Claude Code Must-Haves January 2026 (DEV)](https://dev.to/valgard/claude-code-must-haves-january-2026-kem)
- [CLAUDE.md Organization in Monorepo (DEV)](https://dev.to/anvodev/how-i-organized-my-claudemd-in-a-monorepo-with-too-many-contexts-37k7)
- [Polyrepo Synthesis with Claude Code](https://rajiv.com/blog/2025/11/30/polyrepo-synthesis-synthesis-coding-across-multiple-repositories-with-claude-code-in-visual-studio-code/)
- [Multi-Repo Context Loading (Black Dog Labs)](https://blackdoglabs.io/blog/claude-code-decoded-multi-repo-context)
- [Claude Code Customization Guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)
- [How I Use Every Claude Code Feature](https://blog.sshh.io/p/how-i-use-every-claude-code-feature)

### Tools & Repositories
- [claude-code-configs — Config Composer (GitHub)](https://github.com/Matt-Dionis/claude-code-configs)
- [claude-code-typescript-hooks (GitHub)](https://github.com/bartolli/claude-code-typescript-hooks)
- [claude-code-lsps — LSP Plugin Marketplace (GitHub)](https://github.com/Piebald-AI/claude-code-lsps)
- [awesome-claude-code (GitHub)](https://github.com/hesreallyhim/awesome-claude-code)
- [awesome-claude-code-subagents (GitHub)](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [awesome-claude-skills (GitHub)](https://github.com/travisvn/awesome-claude-skills)

### Vercel Integration
- [Vercel Agent Skills (GitHub)](https://github.com/vercel-labs/agent-skills)
- [Vercel Official MCP Server Documentation](https://vercel.com/docs/mcp/vercel-mcp)
- [Introducing React Best Practices (Vercel Blog)](https://vercel.com/blog/introducing-react-best-practices)
- [Vercel Releases Agent Skills (MarkTechPost)](https://www.marktechpost.com/2026/01/18/vercel-releases-agent-skills-a-package-manager-for-ai-coding-agents-with-10-years-of-react-and-next-js-optimisation-rules/)
- [Vercel Launches Skills — "npm for AI Agents" (Dev Genius)](https://blog.devgenius.io/vercel-launches-skills-npm-for-ai-agents-with-react-best-practices-built-in-452243ea5147)
- [How to Use Vercel Agent-Skills (APIDog)](https://apidog.com/blog/vercel-agent-skills/)
- [Next.js + Vercel + Claude Code Integration (AITMPL)](https://www.aitmpl.com/blog/nextjs-vercel-claude-code-integration/)
- [Community Vercel MCP (GitHub)](https://github.com/nganiet/mcp-vercel)
- [v0 MCP Server (GitHub)](https://github.com/hellolucky/v0-mcp)

### Skills Marketplace (skills.sh)
- [skills.sh — The Open Agent Skills Directory](https://skills.sh/)
- [skills.sh Documentation](https://skills.sh/docs)
- [skills.sh FAQ](https://skills.sh/docs/faq)
- [Agent Skills Standard (agentskills.io)](https://agentskills.io/)
- [Anthropic Official Skills Repository (GitHub)](https://github.com/anthropics/skills)
- [Vercel just launched skills.sh, and it already has 20K installs (Medium)](https://jpcaparas.medium.com/vercel-just-launched-skills-sh-and-it-already-has-20k-installs-c07e6da7e29e)
- [Learn How to Use Skills (Claude Skills) in 5 Minutes (Medium)](https://tonylixu.medium.com/learn-how-to-use-skills-claude-skills-in-5-minutes-e54e5a9aae88)
- [Claude Skills and CLAUDE.md: a practical 2026 guide for teams (Gend.co)](https://www.gend.co/blog/claude-skills-claude-md-guide)
- [How to Make Claude Code Skills Activate Reliably (Scott Spence)](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)
- [Claude Code Has a Skills Marketplace Now — A Beginner-Friendly Walkthrough (Medium)](https://medium.com/@markchen69/claude-code-has-a-skills-marketplace-now-a-beginner-friendly-walkthrough-8adeb67cdc89)

### Original Habr Article
- [Claude Code: Complete Setup Guide (Habr, Russian)](https://habr.com/ru/articles/987094/)
