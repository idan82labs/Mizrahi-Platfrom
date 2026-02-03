---
paths:
  - "frontend/**/*.ts"
  - "frontend/**/*.tsx"
---

# TypeScript Rules

Rules for TypeScript and React code in the frontend.

## Type Safety

- Avoid `any` — use `unknown` if type is truly unknown
- Explicit return types on exported functions
- Use `interface` for object shapes, `type` for unions/intersects
- Prefer `T | null` over `T | undefined` for optional values

## React Components

- Functional components only — no class components
- Use PascalCase for component names and files
- Props interface: `interface ComponentNameProps {}`
- Destructure props in function signature

```tsx
// Preferred
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export function Button({ label, onClick }: ButtonProps): JSX.Element {
  return <button onClick={onClick}>{label}</button>;
}
```

## Hooks

- Custom hooks must start with `use` prefix
- Keep hooks focused on single responsibility
- Extract complex logic from components into hooks
- Specify dependency arrays completely

## State Management

- React Query for server state (API data)
- useState for simple local state
- useReducer for complex local state
- Avoid prop drilling — use context or composition

## Imports

```typescript
// 1. React
import { useState, useEffect } from "react";

// 2. External libraries
import { useQuery } from "@tanstack/react-query";

// 3. Internal - components
import { Button } from "@/components/ui/button";

// 4. Internal - utilities
import { cn } from "@/lib/utils";

// 5. Types
import type { User } from "@/types";
```

## Path Aliases

- Use `@/` for imports from `src/`
- Never use relative paths going up more than one level

## Patterns

### Conditional Rendering

```tsx
// Preferred
{
  isLoading && <Spinner />;
}
{
  error && <ErrorMessage error={error} />;
}
{
  data && <DataDisplay data={data} />;
}
```

### Event Handlers

```tsx
// Inline for simple handlers
<button onClick={() => setCount(c => c + 1)}>

// Extract for complex handlers
const handleSubmit = useCallback((e: FormEvent) => {
  e.preventDefault();
  // complex logic
}, [dependencies]);
```
