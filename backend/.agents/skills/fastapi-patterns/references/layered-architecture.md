# Layered Architecture (Clean Architecture)

## Layer map

```
backend/app/
├── api/v1/             # HTTP layer — FastAPI route handlers
│   ├── auth.py         # POST /auth/login, POST /auth/register, GET /auth/me, etc.
│   ├── expenses.py     # CRUD + analytics + installment endpoints
│   └── categories.py   # Category CRUD
├── schemas/            # DTOs / validation
│   ├── common.py       # BaseResponse, PaginatedResponse
│   ├── expense.py      # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   └── user.py         # UserCreate, UserLogin, UserResponse
├── domains/            # Business logic & interfaces
│   ├── repositories/   # Abstract repository interfaces + IUnitOfWork
│   │   ├── expense.py
│   │   ├── category.py
│   │   ├── credit_card.py
│   │   ├── debt.py
│   │   ├── user.py
│   │   └── unit_of_work.py
│   └── services/       # Business logic implementations
│       ├── expense_service.py
│       ├── installment_service.py
│       ├── analytics_service.py
│       └── category_service.py
├── infrastructure/     # Concrete implementations
│   └── repositories/   # SQLAlchemy implementations
│       ├── expense.py
│       ├── category.py
│       ├── credit_card.py
│       ├── debt.py
│       ├── user.py
│       └── unit_of_work.py
├── models/             # SQLAlchemy ORM entities
│   └── __init__.py     # All entities in one file
├── core/               # Cross-cutting concerns
│   ├── config.py       # Settings (pydantic-settings)
│   ├── security.py     # JWT + bcrypt
│   ├── exceptions.py   # Exception classes + global handlers
│   ├── logging.py      # Loguru setup
│   └── middleware.py   # Security headers
├── db/
│   └── session.py      # Engine, sessionmaker, get_db
└── dependencies/
    ├── auth.py         # get_current_user, get_current_active_user, require_admin
    ├── services.py     # Service DI factory functions
    └── unit_of_work.py # UoW DI factory
```

## Dependency direction

```
api/v1/  →  domains/services/  →  domains/repositories/  ←  infrastructure/repositories/
   ↓              ↓                        ↓
schemas/      models/                  models/
   ↓              ↓                        ↓
core/         core/                     core/
```

- **API** depends on schemas, domains, core — NEVER on infrastructure
- **Domains** depends on models, core — NEVER on API or infrastructure
- **Infrastructure** implements domain interfaces — NEVER referenced by domain
- **Core** is leaf — no project imports

## Adding a new feature

1. Define model in `models/__init__.py`
2. Define repository interface in `domains/repositories/`
3. Add repository to `IUnitOfWork` interface + `SQLAlchemyUnitOfWork` implementation
4. Implement SQLAlchemy repo in `infrastructure/repositories/`
5. Write business logic service in `domains/services/`
6. Wire DI in `dependencies/services.py`
7. Create route handlers in `api/v1/`
8. Add Pydantic schemas in `schemas/`
9. Add typed exceptions in `core/exceptions.py` if needed
10. Add migration SQL file in `migrations/sql/`
