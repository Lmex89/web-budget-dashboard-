# Family Budget - Backend API

FastAPI application following Clean Architecture and SOLID principles.

## Tech stack

- **Runtime:** Python 3.13+
- **Framework:** FastAPI 0.115
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** MariaDB 10.11+
- **Auth:** JWT (HttpOnly cookies) + bcrypt
- **Validation:** Pydantic 2
- **Logging:** Loguru
- **Testing:** pytest + pytest-asyncio (no tests present yet)

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

## API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
