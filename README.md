# Family Budget Web Application

A production-ready monorepo for managing family finances, built with Clean Architecture principles.

## Tech Stack

- **Backend:** Python 3.13+, FastAPI, SQLAlchemy 2.0, MariaDB 10.11+
- **Frontend:** Vue.js 3, Vite, Tailwind CSS, DaisyUI, Pinia
- **Infra:** Docker, Docker Compose

## Project Structure

```
.
├── backend/            # FastAPI Clean Architecture backend
│   ├── app/            # Application code
│   ├── migrations/     # Raw SQL migrations
│   └── tests/          # Test suite (currently empty)
├── frontend/           # Vue 3 SPA frontend
├── docker-compose.yml  # Local development orchestration
└── docs/               # Placeholder for future ADRs / documentation
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

## Backend Architecture

Follows Clean Architecture / Layered Architecture with Unit of Work pattern:
- `domains/`: Business logic, entities, and repository interfaces
- `infrastructure/`: Concrete implementations (SQLAlchemy repos, DB config)
- `api/`: FastAPI route handlers (thin layer)
- `core/`: Shared config, exception handling, security, logging
- `schemas/`: Pydantic DTOs

### Unit of Work Pattern

The backend uses the Unit of Work pattern for transaction management:
- Services depend on `IUnitOfWork` abstraction
- UoW coordinates multiple repositories in a single transaction
- Automatic commit/rollback via context manager

## Database Migrations

Migrations are managed using raw SQL files in `backend/migrations/sql/`:
- Files are numbered sequentially (001_, 002_, etc.)
- Run with: `cd backend && python -m migrations.run_migrations`
- MariaDB 10.11+ is the database engine

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

## License

MIT
