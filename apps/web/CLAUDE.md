# Frontend: React + TypeScript + Vite

This is the web application for the Mizrahi Compliance Platform.

## Tech Stack

- React 18.3 with TypeScript 5.8
- Vite 5.4 (SWC compiler)
- TailwindCSS 3.4 with custom theme
- shadcn/ui components (Radix primitives)
- React Query for server state
- React Hook Form + Zod for forms
- React Router v6 for routing

## Directory Structure

```
src/
├── pages/           # Route components (Index, ToolMonthly, etc.)
├── components/      # Reusable components
│   └── ui/          # shadcn/ui primitives (60+ components)
├── hooks/           # Custom React hooks
├── lib/             # Utilities (utils.ts)
└── assets/          # Static assets
```

## Commands

- `pnpm dev` — Start dev server (http://localhost:5173)
- `pnpm build` — Production build
- `pnpm lint` — Run ESLint
- `pnpm preview` — Preview production build

## Code Conventions

### Components
- Functional components only
- Use PascalCase for component files and names
- Colocate styles with components
- Extract reusable logic into custom hooks

### Imports
- Use `@/` path alias: `import { Button } from "@/components/ui/button"`
- Group: react → external libs → internal → types → styles

### TypeScript
- Explicit return types on exported functions
- Use `interface` for object shapes, `type` for unions/intersects
- Avoid `any` - use `unknown` if type is truly unknown

### State Management
- React Query for server state (API data)
- Local state with useState/useReducer
- Form state with React Hook Form

### Styling
- TailwindCSS utility classes
- Use `cn()` helper for conditional classes
- Custom theme defined in tailwind.config.ts
- Dark mode via `next-themes` (class-based)

## shadcn/ui Usage

Components are in `src/components/ui/`. Add new ones with:
```bash
npx shadcn@latest add <component-name>
```

Available components: button, card, dialog, dropdown-menu, form, input, select, table, tabs, toast, tooltip, and 50+ more.

## API Integration

Use React Query for all API calls:
```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['hooks'],
  queryFn: () => fetch('/api/hooks').then(res => res.json())
});
```

API base URL configured via environment variable.

## Pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | Index | Home page with tool cards |
| `/tool-monthly` | ToolMonthly | Monthly report validation |
| `/tool-matched` | ToolMatched | Special transactions validation |
| `/tool-financial` | ToolFinancial | Financial report (future) |
| `*` | NotFound | 404 page |

## Hebrew Content

- UI labels support Hebrew (RTL)
- Fund manager names displayed in Hebrew
- Use proper font (Heebo) configured in tailwind

## Testing

- Use Vitest for unit tests (planned)
- Test file naming: `Component.test.tsx`
- Run with: `pnpm test`
