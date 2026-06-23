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
>
> **Docker env:** All sensitive config for Docker Compose lives in `/.env.docker` at the project root. Edit that file for Docker DB credentials, JWT secret, etc.

## Domain structure

```
backend/app/
├── api/v1/             # Thin route handlers — NO business logic
├── schemas/            # Pydantic DTOs
├── domains/
│   ├── repositories/   # Abstract interfaces + IUnitOfWork
│   └── services/       # Business logic (ExpenseService, CategoryService, ...)
├── infrastructure/
│   └── repositories/   # SQLAlchemy implementations
├── models/             # ORM entities (__init__.py)
├── core/               # Cross-cutting (config, security, exceptions, logging)
├── db/                 # Engine + session
└── dependencies/       # FastAPI Depends wiring
```

## Adding a new feature

1. Model → 2. Repository interface → 3. Add to UoW → 4. SQLAlchemy impl → 5. Service → 6. DI wiring → 7. Route → 8. Schema → 9. Exception (if needed) → 10. Migration SQL

## Soft delete (required)

- All models **must** include a `deleted_at` column (`Mapped[datetime | None]`).
- Repository `delete()` **must** set `deleted_at = datetime.utcnow()` — never `self.db.delete(obj)`.
- Every query method **must** add `.where(model.deleted_at.is_(None))` to hide soft-deleted rows.
- Implement a private `_active_filter(self)` helper in each repository that returns the filter condition, and reuse it in every query.
- Migration SQL must include `ALTER TABLE ... ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL` for any new table.

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
| `app/domains/services/expense_service.py` | Expense CRUD + CSV export (`list_by_family_csv`) |
| `app/domains/services/category_service.py` | Category business logic (list/create/update) |
| `app/domains/services/debt_service.py` | Debt business logic (list/create) |
| `app/api/v1/expenses.py` | Good vertical slice example (CRUD, analytics, CSV export) |
| `app/api/v1/debts.py` | Debt API endpoints (list/create) |
| `app/api/v1/categories.py` | Category API endpoints (list/create/update) |
| `app/domains/repositories/expense.py` | Expense repository interface (includes `get_by_family_csv`) |
| `app/infrastructure/repositories/expense.py` | SQLAlchemy expense repository implementation |
| `app/models/__init__.py` | All ORM models |
| `migrations/sql/` | Numbered raw SQL files |
