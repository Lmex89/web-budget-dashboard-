# Family Budget Web Application

A production-ready monorepo for managing family finances, built with Clean Architecture principles.

## Tech Stack

- **Backend:** Python 3.13+, FastAPI, SQLAlchemy 2.0, MariaDB 10.11+
- **Frontend:** Vue.js 3, Vite, Tailwind CSS, Pinia, Vue Router 4
- **Infra:** Docker, Docker Compose

## Features

- **Dashboard Overview** — Mobile-first responsive dashboard with expense summary, category breakdown (stacked bar), recent expenses, and top categories.
- **Expense Management** — Create, read, update, and delete expenses with installment support.
- **Categories** — Organize spending with custom categories; edit category names inline.
- **Credit Cards** — Track card limits, closing days, and balances.
- **Debts** — Manage family loans and IOUs with counterparty tracking.
- **Family Sharing** — Multi-user families with JWT-based authentication (Bearer token + HttpOnly cookie fallback, 30-day token expiry).
- **Role-based Access** — Simple RBAC with three roles: `admin`, `member`, `viewer`.

## Project Structure

```
.
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/             # HTTP route handlers
│   │   ├── core/               # Configuration, security, exceptions, logging
│   │   ├── db/                 # Async SQLAlchemy engine and tenant guard
│   │   ├── dependencies/       # FastAPI dependency injection wiring
│   │   ├── domains/
│   │   │   ├── repositories/   # Repository and Unit of Work interfaces
│   │   │   └── services/       # Domain business logic
│   │   ├── infrastructure/
│   │   │   └── repositories/   # SQLAlchemy repository implementations
│   │   ├── models/             # ORM entities
│   │   └── schemas/            # Pydantic request and response DTOs
│   ├── migrations/sql/         # Numbered raw SQL migrations
│   └── tests/                  # Backend test suite
├── frontend/                   # Vue 3 + Vite web SPA
│   └── src/
│       ├── components/         # Shared and feature UI components
│       ├── composables/        # Reusable Composition API logic
│       ├── router/              # Routes and navigation guards
│       ├── services/            # Axios API client
│       ├── stores/              # Pinia application state
│       ├── views/               # Route-level pages
│       ├── types/               # Shared TypeScript types
│       └── utils/               # Formatting and UI utilities
├── mobile/                     # React Native mobile client
│   └── src/
│       ├── app/                 # Navigation and providers
│       ├── components/          # Reusable mobile UI
│       ├── hooks/               # Data and behavior hooks
│       ├── screens/             # Mobile screens
│       ├── services/            # Mobile API client
│       └── stores/              # Mobile state stores
├── docker-compose.yml          # Local development orchestration
├── backup-db.sh                # Database backup script
└── restore-db.sh               # Database restore script
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose
- Python 3.13+ (for local backend development)
- Node.js 20+ and npm (for local frontend development)

## Quick Start

```bash
# 1. Start all services (dev mode with hot-reload)
docker compose up -d

# 2. Start in production mode (nginx-served frontend on port 92)
docker compose --env-file .env.docker --profile prod up -d

# 3. Run database migrations
docker compose exec backend python -m migrations.run_migrations

# 4. Open frontend (dev)
# http://localhost:5173

# 5. API docs (auto-generated)
# http://localhost:8000/docs

# 6. Frontend validation (from frontend/)
npm run typecheck
npm run test
npm run build
```

## First Time Setup

```bash
# 1. Create config from template (edit secrets if needed)
cp .env.docker.example .env.docker

# 2. Start all services
docker compose up -d

# 3. Run database migrations
docker compose exec backend python -m migrations.run_migrations

# 4. Seed default admin user (email: admin@family.com / password: admin123)
docker compose exec backend python -m migrations.seed

# 5. Open the app
# http://localhost:5173
```

> To rebuild from scratch: `docker compose down -v && docker compose up -d --build && docker compose exec backend python -m migrations.run_migrations && docker compose exec backend python -m migrations.seed`

## Architecture Structure

The application is organized as a client-server system. Both clients use the
FastAPI API, while the backend isolates business rules from HTTP and database
details:

```text
Web client (Vue)       Mobile client (React Native)
         \                    /
          \                  /
           ---- HTTP/JSON ----
                    |
             API routes (FastAPI)
                    |
          Schemas and dependencies
                    |
             Domain services
                    |
       Repository interfaces + Unit of Work
                    |
       SQLAlchemy repository implementations
                    |
             MariaDB database
```

### Backend Architecture

Follows Clean Architecture / Layered Architecture with Unit of Work pattern:
- `api/`: FastAPI route handlers; HTTP-only and kept thin
- `schemas/`: Pydantic request and response DTOs
- `domains/services/`: Business rules and transaction orchestration
- `domains/repositories/`: Database-independent repository contracts and `IUnitOfWork`
- `infrastructure/repositories/`: SQLAlchemy implementations of repository contracts
- `models/`: SQLAlchemy ORM entities
- `dependencies/`: FastAPI dependency injection and service wiring
- `db/`: Database sessions and the optional global tenant guard
- `core/`: Shared configuration, security, exceptions, logging, and tenant context

Tenant identity comes from the authenticated user's `family_id`. Services pass
that value to repository operations; clients must not supply or override it.

### Frontend Architecture

- `views/` compose route-level pages from reusable components.
- `stores/` hold shared feature state and call the API service.
- `services/api.ts` centralizes Axios configuration and authentication handling.
- `components/` contains shared UI and feature-specific presentation logic.
- `composables/` and `utils/` contain reusable client-side behavior and formatting.

### Mobile Architecture

- `screens/` define route-level mobile experiences.
- `components/` provide reusable React Native UI.
- `hooks/` encapsulate API-backed data behavior.
- `services/` centralize API communication.
- `app/` owns navigation and global providers.

### Unit of Work Pattern

The backend uses the Unit of Work pattern for transaction management:
- Services depend on `IUnitOfWork` abstraction
- UoW coordinates multiple repositories in a single transaction
- Automatic commit/rollback via context manager

## Roles and Permissions

- `admin`: full access, including family user management and audit logs
- `member`: can create/update/delete budget data, cannot manage users
- `viewer`: read-only across budget data

Family registration creates the first user as `admin`. Additional users default to
`member` unless the admin selects another role when inviting them.

## Database Migrations

Migrations are managed using raw SQL files in `backend/migrations/sql/`:
- Files are numbered sequentially (001_, 002_, etc.)
- Run with: `cd backend && python -m migrations.run_migrations`
- MariaDB 10.11+ is the database engine

## Database Backup & Restore

`backup-db.sh` dumps the DB to `./backups/` (30-day retention) and, when rclone
is installed and B2 credentials are set, also uploads the dump to a Backblaze B2
bucket (`lmex-backups-db/web-budget-family/`) with the same 30-day retention. If
rclone or the credentials are missing, the script logs a warning and keeps the
local backup — the job never fails because of the cloud step.

```bash
# Manual backup (dumps to ./backups/, then uploads to Backblaze B2 if configured)
./backup-db.sh

# List available backups
./restore-db.sh

# Restore from a specific backup
./restore-db.sh backups/family_budget_20260715_020000.sql.gz

# Cron job (daily at 2:00 AM)
# Note: cron runs with minimal PATH, so set it at the top of crontab:
crontab -e

# Add these lines:
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 2 * * * /path/to/web-budget-dashboard-/backup-db.sh >> /path/to/web-budget-dashboard-/backups/cron.log 2>&1
```

### Backblaze B2 cloud backup setup

1. Install rclone on the host: `curl https://rclone.org/install.sh | sudo bash` (or your package manager)
2. Create a bucket named `lmex-backups-db` at https://secure.backblaze.com (10GB free tier)
3. Create an Application Key under **App Keys** (keep both values)
4. Fill these in `.env.docker` (gitignored):

```bash
BACK_BLAZE_KEY_ID=<B2 Application Key ID, e.g. 003a…>
BACK_BLAZE_SECRET=<B2 Application Key, e.g. K005…>
BACK_BLAZE_BUCKET=lmex-backups-db
BACK_BLAZE_DIR=web-budget-family
```

> Note: Backblaze requires **both** the Application Key ID and the secret.
> `BACK_BLAZE_KEY_ID` is the long alphanumeric ID (often starting with `00`),
> not the `K005…` secret itself.

## Local Development

```bash
# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create a local .env file (see .env.example)
cp .env.example .env
# Edit .env if needed; the default connects to the Docker Compose DB on host port 3308.

# Run migrations
python -m migrations.run_migrations

# Start backend dev server
uvicorn app.main:app --reload

# Frontend setup (in a separate terminal)
cd frontend
npm install
npm run dev
```

## Git Commit Conventions

This project follows **Conventional Commits**:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
- **Scope:** area of codebase (`dashboard`, `categories`, `auth`, `backend`, `frontend`)
- **Description:** imperative mood, lowercase, no trailing period
- **Example:** `feat(categories): add inline name editing from categories route`

## License

MIT
