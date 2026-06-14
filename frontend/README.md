# Family Budget - Frontend

Vue 3 SPA for managing family finances.

## Tech stack

- **Framework:** Vue 3 (Composition API + `<script setup>`)
- **Build:** Vite 5
- **Styling:** Tailwind CSS 3 + DaisyUI 4
- **State:** Pinia
- **Routing:** Vue Router 4 (lazy-loaded views)
- **HTTP:** Axios (with 401 interceptor for JWT expiry)

## Project structure

```
src/
├── components/        # Reusable components
│   └── layout/        # App shell (Sidebar, Navbar, MainLayout)
├── router/            # Vue Router config with lazy loading
├── services/          # Axios instance + API client
├── stores/            # Pinia stores (auth, expenses)
├── types/             # TypeScript interfaces
├── views/             # Page-level components (lazy-loaded)
│   ├── Auth/          # Login, Register
│   ├── Dashboard/     # Main analytics view
│   ├── Expenses/      # Expense CRUD
│   ├── Categories/    # Category management
│   ├── CreditCards/   # Credit card tracking
│   ├── Debts/         # Debt management
│   └── Settings/      # Settings view
├── App.vue            # Root component
├── main.ts            # App entry point
└── style.css          # Tailwind imports
```

## Architecture decisions

### State management (Pinia)
- **auth store**: Current user session, login/logout actions
- **expenses store**: Expense list, CRUD operations, analytics data

### Axios interceptors
- 401 responses trigger automatic redirect to `/login`
- Credentials (cookies) are sent with every request via `withCredentials: true`

### Lazy loading
- All route views use dynamic `import()` for code-splitting

## Commands

```bash
npm install      # Install dependencies
npm run dev      # Start dev server (hot reload)
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # ESLint check
npm run typecheck # TypeScript check
```
