# Backend AGENTS.md

See [root AGENTS.md](../AGENTS.md) and the [README architecture structure](../README.md#architecture-structure)
for architecture boundaries, service layer rules, transaction conventions, logging,
auth, and migration caveats. This file adds backend-specific instructions only.

## Fast commands

- Run tests: `pytest`
- Run smoke tests (requires DB + seed): `pytest tests/test_smoke_dashboard.py -v`
- Run locally (venv active): `uvicorn app.main:app --reload`
- Run migrations: `python -m migrations.run_migrations`
- Seed admin user: `python -m migrations.seed`
- Lint: `ruff check .`
- Type check: `mypy app/`

## Runtime dependencies

- FastAPI `0.141.1`, Pydantic `2.13.5`, Uvicorn `0.54.0`, and Loguru `0.7.3` are pinned in `requirements.txt`.

> **Local `.env` required.** Copy `.env.example` → `.env` and adjust `DATABASE_URL` port to `3308`.

## ORM loading (required)

- Relationships default to `lazy="raise"` — load them explicitly per query with `selectinload`/`joinedload` in `infrastructure/repositories/`.
- Never add `lazy="selectin"` to a collection: eager loading cascades across the object graph and turns a single request into 20+ SELECTs (see the smoke-test query budgets).
- The only eager exceptions are `Budget.categories` (`selectin`, bounded) and `BudgetCategory.category` (`joined`).
- New query methods returning ORM entities must preload exactly what the route or serializer touches.

## SQL enum mapping (required)

- MariaDB enum columns store lowercase values (`'pending'`, `'we_owe'`). Every `mapped_column(Enum(...))` must pass `values_callable=lambda obj: [e.value for e in obj]` so SQLAlchemy reads/writes values instead of member names.

## Smoke tests

- `pytest tests/test_smoke_dashboard.py -v` exercises every dashboard endpoint against the real DB plus write round-trips (expense/installment, budget, debt) and bounded SQL counts. Run it after any backend change.
- Requires `backend/.env` (MariaDB on `localhost:3308`) and the seeded admin (`python -m migrations.seed`).
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
- Unique keys on soft-deletable rows (e.g. `uq_budgets_family_period`) still cover deleted rows, so re-inserting after a soft delete raises `IntegrityError`. Expose an `include_deleted` lookup on the repository and restore the existing row (`deleted_at = None`) instead of inserting — see `BudgetRepository.get_by_period` / `BudgetService.upsert`.

## Multi-tenancy (required)

- Every authenticated user belongs to **exactly one family** (`User.family_id`). Tenant identity comes ONLY from `current_user.family_id` — never trust a client-supplied family id.
- Every tenant-owned model carry a `family_id` col (`expenses`, `categories`, `credit_cards`, `debts`).
- Cross-family object access must return **404** (NotFoundException), not 403, to avoid resource enumeration.
- Service methods must always take `family_id` and validate ownership before read/update/delete.
- Global tenant guard: `app/db/tenant_guard.py` registers a `do_orm_execute` listener (on ORM `Session`) injecting `with_loader_criteria` (`family_id == active`) into every SELECT on tenant models. Gated by `ENABLE_GLOBAL_TENANT_GUARD`. Active family set in `get_current_user`, cleared by `app/dependencies/tenant.py::tenant_scope` (global dependency). Do NOT add `User`/`Installment`/`AuditLog`/`BudgetCategory` to the guarded set (auth needs cross-family user reads; the rest have no `family_id` and are reached only through tenant-owned relations). `Budget` is guarded because it carries `family_id`.
- Per-request context lives in `app/core/tenant.py` (`set_tenant_context` / `get_tenant_context` / `clear_tenant_context`).
- Add tenant-scoped composite indexes (lead with `family_id`) in new migrations, e.g. `migrations/sql/012_add_tenant_composite_indexes.sql`.

## Relevant skills

- `.agents/skills/fastapi-patterns/` — authoritative backend patterns guide

## Key files

| File | What it is |
|---|---|
| `app/main.py` | App bootstrap |
| `app/core/config.py` | Settings (env defaults) |
| `app/core/security.py` | JWT + bcrypt |
| `app/core/exceptions.py` | All exception classes + global handlers |
| `app/core/serialization.py` | `to_jsonable` Decimal→float helper for raw-dict API responses (budgets, analytics) |
| `app/dependencies/auth.py` | Auth + role-based authorization dependencies (`require_roles`, sets tenant context) |
| `app/db/session.py` | Engine, sessionmaker, `get_db` |
| `app/db/tenant_guard.py` | Global SQLAlchemy tenant guard (feature-flagged `with_loader_criteria`) |
| `app/core/tenant.py` | Per-request tenant context (contextvar) |
| `app/dependencies/tenant.py` | `tenant_scope` global dependency (clears tenant context after request) |
| `app/dependencies/services.py` | Service DI factory functions |
| `app/domains/services/expense_service.py` | Expense CRUD + CSV export (`list_by_family_csv`) |
| `app/domains/services/budget_service.py` | Monthly budget upsert, category-limit sync, progress computation |
| `app/domains/repositories/budget.py` | Budget repository interface |
| `app/infrastructure/repositories/budget.py` | SQLAlchemy budget repository implementation |
| `app/api/v1/budgets.py` | Budget API endpoints (list, progress, upsert, delete) |
| `app/domains/services/category_service.py` | Category business logic (list/create/update/delete) |
| `app/domains/services/debt_service.py` | Debt business logic (list/create) |
| `app/api/v1/expenses.py` | Good vertical slice example (CRUD, analytics, CSV export) |
| `app/api/v1/debts.py` | Debt API endpoints (list/create) |
| `app/api/v1/categories.py` | Category API endpoints (list/create/update/delete) |
| `app/domains/repositories/expense.py` | Expense repository interface (includes `get_by_family_csv`) |
| `app/infrastructure/repositories/expense.py` | SQLAlchemy expense repository implementation |
| `app/models/__init__.py` | All ORM models |
| `migrations/sql/` | Numbered raw SQL files |
