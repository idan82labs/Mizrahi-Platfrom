# Coding Style

General code quality rules for the entire codebase.

## Readability

- Prefer early returns over deep nesting
- Max function length: 50 lines — split if larger
- Max file length: 300 lines — split if larger
- Functions do one thing — if the name has "and", split it
- No magic numbers — use named constants
- Keep indentation depth ≤ 3 levels

## Naming

- Be descriptive but concise
- Boolean variables/functions: use `is`, `has`, `should`, `can` prefixes
- Functions: use verbs (`getUser`, `validateInput`, `sendEmail`)
- Constants: UPPER_SNAKE_CASE
- Avoid abbreviations unless universally understood

## Comments

- Only add comments for "why", never for "what"
- Don't add docstrings/comments to code you didn't change
- Remove commented-out code — use git history instead
- TODO comments must include context or ticket reference

## Imports

- Group imports: stdlib → external → internal → types
- Sort alphabetically within groups
- No unused imports
- Prefer specific imports over wildcard (`*`)

## Error Handling

- Handle errors at appropriate boundaries
- Don't swallow errors silently
- Log errors with context
- Use specific exception types, not generic `Exception`

## Code Organization

- Keep related code together
- Extract reusable logic into functions/utilities
- Avoid circular dependencies
- Prefer composition over inheritance
