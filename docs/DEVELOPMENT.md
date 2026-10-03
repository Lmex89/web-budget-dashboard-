# Development Guide

Local workflows, ports, and hot-reload setup for the Family Budget monorepo.
See [README.md](../README.md) for the project overview and architecture.

## Ports

| Service | URL |
|---|---|
| Web frontend (Docker nginx or Vite dev server) | http://localhost:5173 |
| Backend API (Docker) | http://localhost:8003 |
| Backend API (local uvicorn) | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8003/docs |
| MariaDB (host port) | localhost:3308 |

## Environment files

| File | Used by | Notes |
|---|---|---|
| `.env.docker` | Docker Compose services (runtime) | Gitignored; copy from `.env.docker.example` |
| `.env` | Docker Compose variable interpolation (build args) | Symlink to `.env.docker`: `ln -sf .env.docker .env` |
| `backend/.env` | Local backend | Gitignored; copy from `backend/.env.example` (DB port `3308`) |
| `frontend/.env.local` | Local Vite dev server | Gitignored (`*.local`); set `VITE_API_BASE_URL` |

One-time setup:

```bash
cp .env.docker.example .env.docker   # edit secrets as needed
ln -sf .env.docker .env
```

## Option A — Docker backend + local Vite frontend (recommended)

Hot reload on both backend and frontend.

```bash
docker compose up -d db backend

cd frontend
npm install
printf 'VITE_API_BASE_URL=http://localhost:8003\n' > .env.local
npm run dev
```

Open http://localhost:5173. Requests go directly to the backend on port 8003.

- Backend reloads on save (`uvicorn --reload`, `./backend` bind-mounted).
- Vite hot-reloads instantly. Restart it after editing `.env.local` — Vite only reads env files at startup.

## Option B — Fully local backend

```bash
docker compose up -d db

cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # defaults to localhost:3308
python -m migrations.run_migrations
python -m migrations.seed        # first time only — admin@family.com / admin123
uvicorn app.main:app --reload    # http://localhost:8000
```

Point the frontend at the local backend with `frontend/.env.local`:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Tests and validation

| Area | Commands |
|---|---|
| Backend (from `backend/`) | `pytest` |
| Backend email unit tests (no DB) | `pytest tests/test_email.py -v` |
| Frontend (from `frontend/`) | `npm run typecheck`, `npm run test`, `npm run build` |
| Mobile (from `mobile/`) | `npm run typecheck`, `npm run lint` |

`npm run lint` in `frontend/` is currently broken (missing ESLint config); use `typecheck` and `build` for validation.

## Database

```bash
# Apply migrations (from backend/, venv active, Docker DB on 3308)
python -m migrations.run_migrations

# Apply a single migration to a running Docker DB
docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' \
  < backend/migrations/sql/013_create_budgets.sql

# Open a SQL shell
docker compose exec db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"'

# Reset everything (DESTROYS all data)
docker compose down -v && docker compose up -d --build
```

`python -m migrations.run_migrations` re-applies every SQL file in order and is **not** idempotent
(`012_add_tenant_composite_indexes.sql` fails on re-run). For an existing database, apply only the
new SQL file directly.

## Mobile

```bash
cd mobile
npm install
npm start        # Expo dev server — scan the QR code with the Expo Go app
```

The mobile API base URL is currently hardcoded in `mobile/src/services/api.ts`; update it to point
at your backend before running against real data.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Login returns 405, or `/api/...` returns HTML | Frontend bundle was built without `VITE_API_BASE_URL`. Ensure the `.env` symlink exists, then `docker compose up -d --build frontend` |
| Changed `VITE_API_BASE_URL`, app still uses the old URL | Vite bakes it at build time (Docker) or startup (dev server) — rebuild the frontend image or restart `npm run dev` |
| `docker compose` builds with an empty API URL | `.env` symlink is missing (`ln -sf .env.docker .env`) |
