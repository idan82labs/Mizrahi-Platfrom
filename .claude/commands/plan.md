---
description: Create a detailed implementation plan before coding
allowed-tools: Read, Grep, Glob
---

Create a detailed implementation plan for: $ARGUMENTS

Use the planner agent to analyze and create a step-by-step plan.

## Process

1. **Analyze Requirement**
   - Understand what needs to be built
   - Identify scope and constraints
   - Note any ambiguities to clarify

2. **Explore Codebase**
   - Find related implementations
   - Understand current patterns
   - Identify reusable components

3. **Identify Affected Files**
   - List all files that need changes
   - Mark as Create / Modify / Delete
   - Note dependencies between files

4. **Create Implementation Plan**
   - Numbered steps
   - Exact file paths
   - What to add/modify
   - Verification after each step

5. **Identify Risks**
   - Security considerations
   - Performance impacts
   - Breaking changes
   - Testing requirements

## Output Format

```markdown
# Implementation Plan: [Feature Name]

## Summary
[1-2 sentence overview]

## Scope
- [ ] Files to create: X
- [ ] Files to modify: X
- [ ] Estimated complexity: Low/Medium/High

## Affected Files
| File | Action | Purpose |
|------|--------|---------|

## Implementation Steps

### Step 1: [Description]
- File: `path/to/file`
- Changes: [specific changes]
- Verification: [how to verify]

### Step 2: ...

## Testing Plan
- [ ] Unit tests for...
- [ ] Integration tests for...
- [ ] Manual verification of...

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|

## Documentation Updates
- [ ] Update [doc file] if needed
```

## Important

- Do NOT implement — only plan
- Ask for clarification if requirements are unclear
- Consider existing patterns in the codebase
- Plan for incremental testing
