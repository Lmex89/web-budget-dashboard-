# Family Budget - Backend API

FastAPI application following Clean Architecture and SOLID principles.

## Tech stack

- **Runtime:** Python 3.13+
- **Framework:** FastAPI 0.115
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** MariaDB 10.11+
- **Auth:** JWT (Bearer header + HttpOnly cookie fallback) + bcrypt
- **Validation:** Pydantic 2
- **Logging:** Loguru
- **Testing:** pytest + pytest-asyncio (see `tests/`)

## Multi-tenancy

Data is isolated per family in a single shared schema. Each authenticated user
belongs to exactly one family (`User.family_id`), and all tenant-owned models
(`expenses`, `categories`, `credit_cards`, `debts`) carry a `family_id`.

Isolation is enforced in depth:

1. **Service layer** — every read/write takes `family_id` and validates
   ownership; cross-family object access returns **404** (not 403) to avoid
   resource enumeration.
2. **Global SQLAlchemy guard** (feature-flagged) — when
   `ENABLE_GLOBAL_TENANT_GUARD=true`, a `do_orm_execute` listener injects
   `family_id = <active family>` into every SELECT on tenant-owned models via
   `with_loader_criteria`. The active family is set per-request in `get_current_user`
   and cleared by the `tenant_scope` global dependency. `User`, `Installment` and
   `AuditLog` are excluded (auth must read users across families; the latter two
   have no `family_id`).

The `family_id` claim is included in the JWT for observability, but the DB user
lookup in `get_current_user` remains the source of truth for authorization.

## Architecture

### Clean Architecture layers

```
app/
├── api/              # HTTP layer (route handlers only)
├── core/             # Cross-cutting concerns (config, exceptions, security, logging)
├── db/               # Database session factory
├── dependencies/     # FastAPI Depends wiring (auth, UoW, services)
├── domains/          # Business logic
│   ├── services/     #   Service classes (ExpenseService, AnalyticsService, etc.)
│   └── repositories/ #   Repository interfaces (contracts)
├── infrastructure/   # Framework implementations
│   └── repositories/ #   SQLAlchemy repositories
├── models/           # SQLAlchemy ORM models
└── schemas/          # Pydantic DTOs (request/response)
```

### SOLID service layer

| Service | Responsibility |
|---|---|
| `ExpenseService` | CRUD for expenses, validation, family-scoping |
| `InstallmentService` | Installment generation, overdue detection, status tracking |
| `AnalyticsService` | Monthly summaries, category distributions, trends, card utilization |

### Unit of Work pattern

All write operations run inside `async with self.uow:` which:
- Opens a database transaction
- Commits on success or rolls back on exception
- Coordinates multiple repositories in a single transaction

## Commands

```bash
# Development
uvicorn app.main:app --reload          # Start dev server (venv active)
python -m migrations.run_migrations    # Run DB migrations

# Testing
pytest                                 # Run all tests
pytest -v                              # Verbose
```

## Environment variables

Copy `.env.example` to `.env` and adjust as needed. At minimum set `DATABASE_URL` to match your database host/port (e.g., `mysql+aiomysql://budget_user:budget_pass@localhost:3308/family_budget` when using the Docker Compose database).

| Variable | Description | Default |
|---|---|---|
| `ENABLE_GLOBAL_TENANT_GUARD` | Enables the global SQLAlchemy tenant guard (defense-in-depth family filtering) | `false` |

## Database migrations

Add new numbered files under `migrations/sql/` and run
`python -m migrations.run_migrations`. See `migrations/sql/012_add_tenant_composite_indexes.sql`
for tenant-scoped composite indexes on all tenant-owned tables.

## API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
