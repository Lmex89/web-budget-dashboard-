# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project at a glance

- Monorepo: FastAPI backend + Vue frontend + Docker Compose.
- Backend runtime: Python 3.13+.
- Primary project documentation: [README.md](README.md).
- Backend source root: [backend/app](backend/app).
- Database: MariaDB 10.11+ via raw SQL migrations (no Alembic).

## Fast commands

- Start full stack: `docker compose up -d`
- Run backend migrations (from `backend/`): `python -m migrations.run_migrations`
- Run backend locally (from `backend/`, venv active): `uvicorn app.main:app --reload`
- Run frontend locally (from `frontend/`): `npm run dev`
- Run backend tests (from `backend/`): `pytest`

> **Local backend note:** All local backend commands require a `backend/.env` file. The default `DATABASE_URL` in `app/core/config.py` points to `localhost:3306`, but Docker Compose exposes MariaDB on host port `3308`. Copy `backend/.env.example` to `backend/.env` and adjust the port before running migrations or the dev server.

## Architecture boundaries (required)

Follow Clean Architecture boundaries described in [README.md](README.md):

- API layer (HTTP only): [backend/app/api](backend/app/api)
- Domain interfaces and business logic: [backend/app/domains](backend/app/domains)
- Infrastructure implementations: [backend/app/infrastructure](backend/app/infrastructure)
- Shared cross-cutting concerns: [backend/app/core](backend/app/core)
- DTOs/validation: [backend/app/schemas](backend/app/schemas)

Rules:

- Keep route handlers thin. Put business logic in service classes.
- Add repository interfaces in `domains/repositories` and concrete SQLAlchemy implementations in `infrastructure/repositories`.
- Use dependency injection with FastAPI `Depends` (examples in [backend/app/dependencies](backend/app/dependencies)).
- Prefer raising typed app exceptions from [backend/app/core/exceptions.py](backend/app/core/exceptions.py) instead of returning ad-hoc error payloads.

## SOLID Service Layer (required)

Each domain concern gets its own focused service class:

| Service | Responsibility |
|---|---|
| `ExpenseService` | CRUD for expenses, validation, family-scoping |
| `InstallmentService` | Installment generation, overdue detection, status tracking |
| `AnalyticsService` | Monthly summaries, category distributions, trends, card utilization |

Service rules:
- Every service receives `IUnitOfWork` via constructor injection.
- Every mutating method wraps work in `async with self.uow:`.
- Services DO NOT call each other's UoW methods directly — compose via the shared `self.uow`.
- Add new analytics methods to `AnalyticsService`, not to `ExpenseService`.

## Async and transaction conventions

- Backend DB code is async SQLAlchemy; keep new DB logic async (session setup: [backend/app/db/session.py](backend/app/db/session.py)).
- Service methods should operate inside `async with self.uow:` when performing transactional work.
- Preserve Unit of Work pattern:
  - Interface: [backend/app/domains/repositories/unit_of_work.py](backend/app/domains/repositories/unit_of_work.py)
  - Implementation: [backend/app/infrastructure/repositories/unit_of_work.py](backend/app/infrastructure/repositories/unit_of_work.py)

## Logging conventions (required)

- Use `from loguru import logger` in every module — no custom loggers.
- Use f-strings only for log messages: `logger.info(f"User {user_id} created")`.
- Inside `except` blocks, always use `logger.exception(...)` (auto-captures traceback).
- Never use `logger.error("msg", exc_info=True)` — use `logger.exception` instead.
- Log levels:
  - `DEBUG` — SQL queries, parameter dumps
  - `INFO` — CRUD operations, auth events
  - `WARNING` — validation failures, unauthorized access attempts
  - `ERROR` — database failures, unhandled paths
  - `EXCEPTION` — inside `except` blocks only

## Auth, API, and data-shape conventions

- Authentication uses JWT stored in cookie `access_token` (see [backend/app/dependencies/auth.py](backend/app/dependencies/auth.py)).
- Keep API response envelope consistency with schemas in [backend/app/schemas/common.py](backend/app/schemas/common.py).
- Money values use Decimal/Numeric in domain and schema models (see [backend/app/models/__init__.py](backend/app/models/__init__.py) and [backend/app/schemas/expense.py](backend/app/schemas/expense.py)); avoid introducing float math in business logic.
- Custom exception classes are organized by domain in [backend/app/core/exceptions.py](backend/app/core/exceptions.py).

## Migration and schema caveat

- Migrations use raw SQL files in [backend/migrations/sql](backend/migrations/sql).
- Files are numbered sequentially (001_create_families.sql, 002_create_users.sql, ...).
- Run migrations from the `backend/` directory: `python -m migrations.run_migrations`.
- Ensure `DATABASE_URL` is set in `backend/.env` (the runner converts `+aiomysql` to `+pymysql` internally).
- Before changing schema, inspect all SQL files and add a new numbered file.

## High-value files to read before major edits

- App bootstrap: [backend/app/main.py](backend/app/main.py)
- Config and env defaults: [backend/app/core/config.py](backend/app/core/config.py)
- Compose runtime wiring: [docker-compose.yml](docker-compose.yml)
- Expense API flow (good vertical slice): [backend/app/api/v1/expenses.py](backend/app/api/v1/expenses.py)
- Service layer entry point: [backend/app/dependencies/services.py](backend/app/dependencies/services.py)
- Domain models (all entities): [backend/app/models/\_\_init\_\_.py](backend/app/models/__init__.py)
- Exception hierarchy: [backend/app/core/exceptions.py](backend/app/core/exceptions.py)
