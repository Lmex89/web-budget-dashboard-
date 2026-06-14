# Backend AGENTS.md

See [root AGENTS.md](../AGENTS.md) for architecture boundaries, service layer rules,
transaction conventions, logging, auth, and migration caveats. This file adds
backend-specific instructions only.

## Fast commands

- Run tests: `pytest`
- Run locally (venv active): `uvicorn app.main:app --reload`
- Run migrations: `python -m migrations.run_migrations`
- Seed admin user: `python -m migrations.seed`
- Lint: `ruff check .`
- Type check: `mypy app/`

> **Local `.env` required.** Copy `.env.example` → `.env` and adjust `DATABASE_URL` port to `3308`.

## Domain structure

```
backend/app/
├── api/v1/             # Thin route handlers — NO business logic
├── schemas/            # Pydantic DTOs
├── domains/
│   ├── repositories/   # Abstract interfaces + IUnitOfWork
│   └── services/       # Business logic (ExpenseService, InstallmentService, ...)
├── infrastructure/
│   └── repositories/   # SQLAlchemy implementations
├── models/             # ORM entities (__init__.py)
├── core/               # Cross-cutting (config, security, exceptions, logging)
├── db/                 # Engine + session
└── dependencies/       # FastAPI Depends wiring
```

## Adding a new feature

1. Model → 2. Repository interface → 3. Add to UoW → 4. SQLAlchemy impl → 5. Service → 6. DI wiring → 7. Route → 8. Schema → 9. Exception (if needed) → 10. Migration SQL

## Relevant skills

- `.agents/skills/fastapi-patterns/` — authoritative backend patterns guide

## Key files

| File | What it is |
|---|---|
| `app/main.py` | App bootstrap |
| `app/core/config.py` | Settings (env defaults) |
| `app/core/security.py` | JWT + bcrypt |
| `app/core/exceptions.py` | All exception classes + global handlers |
| `app/db/session.py` | Engine, sessionmaker, `get_db` |
| `app/dependencies/services.py` | Service DI factory functions |
| `app/domains/services/debt_service.py` | Debt business logic (list/create) |
| `app/api/v1/debts.py` | Debt API endpoints (list/create) |
| `app/models/__init__.py` | All ORM models |
| `app/api/v1/expenses.py` | Good vertical slice example |
| `migrations/sql/` | Numbered raw SQL files |
