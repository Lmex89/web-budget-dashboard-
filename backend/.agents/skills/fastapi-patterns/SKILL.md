---
name: fastapi-patterns
description: MUST be used for any FastAPI or Python backend task in this repository. Enforces Clean Architecture, SOLID services, Unit of Work pattern, typed exceptions, loguru logging, and raw SQL migrations. Load for any backend API, service, model, migration, or test work.
---

# FastAPI Backend Patterns

Use this skill as the authoritative instruction set for all backend work. Follow the sections in order unless the user explicitly asks otherwise.

## 1) Confirm architecture alignment (required)

This project follows **Clean Architecture** with strict layer boundaries:

| Layer | Directory | Responsibility |
|---|---|---|
| API | `backend/app/api/v1/` | Thin route handlers only |
| Schemas/DTOs | `backend/app/schemas/` | Pydantic validation & serialization |
| Domain (services) | `backend/app/domains/services/` | Business logic |
| Domain (repositories) | `backend/app/domains/repositories/` | Abstract repository interfaces |
| Infrastructure | `backend/app/infrastructure/repositories/` | SQLAlchemy implementations |
| Core | `backend/app/core/` | Config, security, exceptions, logging, middleware |
| Models | `backend/app/models/` | SQLAlchemy ORM entities |

### 1.1 Must-read references (required)

Before any backend implementation, read and apply these:

- `references/layered-architecture.md` — Clean Architecture boundaries, dependency rules
- `references/unit-of-work.md` — Transaction management pattern
- `references/exceptions.md` — Typed exception hierarchy and global handlers
- `references/logging.md` — Loguru conventions

### 1.2 Layer dependency rules (required)

- API layer imports from domains, schemas, core — NEVER from infrastructure
- Domain layer imports from models, core — NEVER from API or infrastructure
- Infrastructure imports domain interfaces — NEVER the reverse
- Core is shared cross-cutting — imported by all layers

## 2) SOLID principles in practice (required)

Each SOLID principle is enforced by architecture, conventions, and tooling:

| Principle | How it's applied in this project | Example |
|---|---|---|
| **S** — Single Responsibility | One class = one concern. Services own one domain lifecycle. Repositories own one entity's persistence. Route handlers only wire HTTP → service. | `ExpenseService` handles expense CRUD; `AnalyticsService` handles aggregation — they are separate classes. |
| **O** — Open for extension, closed for modification | Repository interfaces + DI allow swapping implementations without modifying consumers. New analytics methods are added to `AnalyticsService`, not to `ExpenseService`. | `IUnitOfWork` → `SQLAlchemyUnitOfWork`. To switch DB library, implement `IUnitOfWork` differently — no service code changes. |
| **L** — Liskov Substitution | Repository interface subtypes are substitutable. Any `XxxRepository` impl can replace another without breaking callers. Exceptions follow a strict hierarchy — handlers catch `AppException`, not concrete types. | `ExpenseRepository` (ABC) → `SQLAlchemyExpenseRepository`. Adding a `MockExpenseRepository` for tests requires zero service changes. |
| **I** — Interface Segregation | Each repository interface exposes only the methods its consumers need. `IUnitOfWork` composes multiple fine-grained repositories rather than one god interface. | `ExpenseRepository` has `get_by_family`, `get_family_monthly_summary`; `UserRepository` does not — unrelated consumers are not forced to depend on unused methods. |
| **D** — Dependency Inversion | High-level services depend on abstract `IUnitOfWork` / repository interfaces, not on concrete SQLAlchemy classes. Infrastructure implements domain interfaces; domain never imports infrastructure. | `ExpenseService.__init__(self, uow: IUnitOfWork)` — the service has zero knowledge of SQLAlchemy, sessions, or connection pooling. |

## 3) Apply SOLID service patterns (required)

### 3.1 Service structure

```python
class XxxService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def do_something(self, ...) -> Model:
        logger.info(f"Doing something: ...")
        async with self.uow:
            # validation + business logic
            return await self.uow.xxx_repo.method(...)
```

Rules:
- Every service receives `IUnitOfWork` via constructor injection
- Every mutating method wraps work in `async with self.uow:`
- Read-only methods also use `async with self.uow:` for consistency
- Services DO NOT call each other's UoW methods — compose via shared `self.uow`
- Add domain-specific validators as `_validate_*` private methods

### 3.2 Repository interfaces and implementations

**Interface** (in `domains/repositories/`):
```python
class XxxRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Model]: ...
    @abstractmethod
    async def create(self, model: Model) -> Model: ...
```

**Implementation** (in `infrastructure/repositories/`):
```python
class SQLAlchemyXxxRepository(XxxRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: str) -> Optional[Model]:
        try:
            result = await self.db.execute(select(Model).where(Model.id == id))
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            logger.exception("DB error fetching ...")
            raise AppException("ERR_DATABASE", "...")
```

Rules:
- All DB calls wrapped in try/except with `logger.exception()` and typed `AppException` re-raise
- Use `selectinload` / `joinedload` for eager loading of relationships
- Return domain models (SQLAlchemy ORM instances), NOT dicts

### 3.3 Dependency injection wiring

**UoW provider** (`dependencies/unit_of_work.py`):
```python
async def get_unit_of_work(db: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(db)
```

**Service provider** (`dependencies/services.py`):
```python
def get_xxx_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> XxxService:
    return XxxService(uow)
```

## 4) Factory Pattern (required)

The project uses the **Factory Method** pattern in two forms:

### 4.1 DI factory functions (`dependencies/services.py`)

FastAPI's `Depends` acts as a factory — each `get_*_service()` function creates and returns a service instance with its UoW dependency wired in:

```python
def get_expense_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> ExpenseService:
    return ExpenseService(uow)
```

Add a new factory function for each new service. It is the single place where service construction is defined.

### 4.2 Lazy-init repository factories (`infrastructure/repositories/unit_of_work.py`)

`SQLAlchemyUnitOfWork` lazily instantiates repositories on first access via `@property`:

```python
@property
def expenses(self) -> ExpenseRepository:
    if self._expenses is None:
        self._expenses = SQLAlchemyExpenseRepository(self._session)
    return self._expenses
```

This is a **lazy factory**: repositories are created on-demand, only when the service actually uses them. When adding a new repository:
1. Add `@property` with lazy-init to `SQLAlchemyUnitOfWork`
2. Add abstract property to `IUnitOfWork` interface
3. No other wiring changes needed

### 4.3 When to add a factory

- New FastAPI service dependency → add `get_*_service()` in `dependencies/services.py`
- New domain repository → add lazy property in `SQLAlchemyUnitOfWork + IUnitOfWork`
- NEVER instantiate services or UoW manually in route handlers — always use `Depends`

## 5) Facade Pattern (required)

The **Facade** pattern simplifies complex subsystems behind a unified interface:

### 5.1 `IUnitOfWork` as a domain facade

`IUnitOfWork` provides a single entry point to all repositories, hiding session management, transaction boundaries, and repository instantiation:

```python
# Without facade — service would need to manage session, create repos, handle transactions
async with session.begin():
    repo = SQLAlchemyExpenseRepository(session)
    card_repo = SQLAlchemyCreditCardRepository(session)
    expense = await repo.create(data)
    card = await card_repo.get_by_id(card_id)

# With facade — unified interface, zero infrastructure leak
async with self.uow:
    expense = await self.uow.expenses.create(data)
    card = await self.uow.credit_cards.get_by_id(card_id)
```

The service deals only with `self.uow.repo.method()` — no sessions, no commits, no repository construction.

### 5.2 Service classes as business logic facades

Each service (`ExpenseService`, `InstallmentService`, `AnalyticsService`) is a facade that orchestrates multiple repositories and validators behind a simple method interface:

```python
# Route handler calls ONE service method
expense = await service.create(data, family_id, user_id)

# Inside the facade, multiple subsystems are coordinated:
async with self.uow:
    await self._validate_category(data.category_id, family_id)
    await self._validate_credit_card(data.payment_method, data.credit_card_id, family_id)
    self._validate_installment_config(data)
    expense = Expense(...)
    created = await self.uow.expenses.create(expense)
    if data.is_installment:
        await self.installments.generate(created.id, data.total_installments, data.amount)
```

The route handler is decoupled from validation rules, installment logic, and persistence — all behind the `service.create()` facade.

### 5.3 Rules for facade methods

- Keep the public API small and stable (one method = one business operation)
- Hide all complexity (validation, cross-repository calls, sub-service delegation) inside the facade
- NEVER expose session, UoW internals, or repository references in the facade's public signature
- Add new facade methods to the appropriate existing service, not as standalone functions

## 6) Apply API patterns (required)

### 6.1 Route handler structure

Routes are **thin** — call a service method, return a response schema:

```python
router = APIRouter(prefix="/things", tags=["Things"])

@router.get("", response_model=PaginatedResponse)
async def list_things(
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_active_user),
    service: XxxService = Depends(get_xxx_service),
):
    logger.info(f"GET /things - user={current_user.id}, page={page}")
    items, total = await service.list_by_family(current_user.family_id, page)
    return PaginatedResponse(data=[...], total=total, page=page, ...)
```

### 6.2 Response envelope

All API responses use the standard envelope from `schemas/common.py`:

- `BaseResponse` — `{"success": true, "data": ...}`
- `PaginatedResponse(BaseResponse)` — adds `total`, `page`, `page_size`, `total_pages`
- Use `ExpenseResponse.model_validate(orm_model)` to convert ORM → Pydantic

### 6.3 Auth dependencies

- `get_current_active_user` — standard authenticated user
- `require_admin` — admin-only routes
- Both raise `UnauthorizedException` / `ForbiddenException` (captured by global handlers)

### 6.4 Money values

- All monetary fields use `Decimal`/`Numeric(15, 2)` in models
- NEVER introduce `float` for monetary calculations
- Cast to `float` only at API boundary for JSON serialization

## 7) Apply database patterns (required)

### 7.1 Models

- All models extend `Base` (DeclarativeBase)
- Primary keys: `String(36)` with `default=lambda: str(uuid.uuid4())`
- Timestamps: `DateTime(timezone=True)` with `utcnow`
- Use `Mapped[]` type annotations throughout
- Use `relationship()` with explicit `lazy=` (prefer `selectin`)

### 7.2 Migrations

- Raw SQL files in `backend/migrations/sql/`, numbered sequentially
- Run via CLI: `mariadb --skip-ssl` (not SQLAlchemy DDL)
- From `backend/` dir: `python -m migrations.run_migrations`
- Add new file, do NOT modify existing migration files

### 7.3 Session management

```python
engine = create_async_engine(settings.DATABASE_URL, pool_size=10, ...)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, ...)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

## 8) Exception handling (required)

### 8.1 Hierarchy

```
AppException (base)
├── NotFoundException (404)
│   ├── ExpenseNotFoundException
│   └── ...
├── UnauthorizedException (401)
│   └── InvalidCredentialsException
├── ForbiddenException (403)
│   └── ExpenseNotInFamilyException
├── ValidationException (422)
│   ├── InvalidCategoryForExpenseException
│   └── InstallmentMisconfigurationException
├── ConflictException (409)
│   └── EmailAlreadyRegisteredException
```

### 8.2 Global handlers (registered in `main.py`)

- `AppException` → 4xx/5xx with `{success, error: {code, message, details}}`
- `RequestValidationError` (Pydantic) → 422 with field-level detail
- `SQLAlchemyError` → 500 with safe error message
- `Exception` → 500 fallback

### 8.3 Raising exceptions

```python
raise NotFoundException("Resource", resource_id)
raise UnauthorizedException("Custom message")
raise ValidationException("Bad input", {"field": "error"})
raise EmailAlreadyRegisteredException(email)
```

## 9) Logging (required)

- `from loguru import logger` in every module
- Use f-strings: `logger.info(f"User {user_id} created")`
- Inside `except` blocks: `logger.exception(...)` (auto-captures traceback)
- NEVER use `logger.error("msg", exc_info=True)` — use `logger.exception`
- Log levels: `DEBUG` (queries), `INFO` (CRUD/auth), `WARNING` (validation/unauth), `ERROR` (DB failures)
- Health check logs are suppressed via `HealthCheckFilter`

## 10) Testing patterns (required)

- Use `pytest` with `httpx.AsyncClient` + `ASGITransport`
- Override dependencies via `app.dependency_overrides`
- Use `pytest-asyncio` for async test functions
- Test files mirror source structure under `tests/`

## 11) Security (required)

- JWT tokens stored in `access_token` HttpOnly cookie
- Password hashing with `passlib` + `bcrypt`
- CORS origins from config (`localhost:5173`, `localhost:3000`)
- JWT decoding raises `UnauthorizedException` on expiry/invalid
- Admin routes guarded by `require_admin`

## 12) Self-check

- [ ] Architecture layer boundaries are respected
- [ ] All mutating methods use `async with self.uow:`
- [ ] All DB calls wrapped in try/except with `logger.exception()`
- [ ] Domain exceptions raised (not raw HTTP responses)
- [ ] Pydantic schemas used for request/response validation
- [ ] Float never used for money calculations
- [ ] loguru logger used in every module
- [ ] `logger.exception()` on all bare `except` blocks
- [ ] f-strings used in log messages
- [ ] Route handlers are thin (no business logic)
- [ ] SOLID principles respected (SRP: one class one concern, DIP: depends on abstractions)
- [ ] Factory functions used for service DI (not manual instantiation)
- [ ] Service facade hides validation, cross-repo calls, and sub-service delegation
- [ ] UoW facade hides session, commits, and repository construction
