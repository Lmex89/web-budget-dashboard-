# Unit of Work Pattern

## Interface (`domains/repositories/unit_of_work.py`)

```python
class IUnitOfWork(ABC):
    expenses: ExpenseRepository
    categories: CategoryRepository
    credit_cards: CreditCardRepository
    debts: DebtRepository
    users: UserRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    @abstractmethod
    async def commit(self) -> None: ...
    @abstractmethod
    async def rollback(self) -> None: ...
    @abstractmethod
    async def close(self) -> None: ...
```

## Implementation (`infrastructure/repositories/unit_of_work.py`)

```python
class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def expenses(self):
        if self._expenses is None:
            self._expenses = SQLAlchemyExpenseRepository(self._session)
        return self._expenses

    # ... lazy-init for all repos

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except Exception:
            logger.exception("Commit failed")
            raise

    async def rollback(self) -> None:
        try:
            await self._session.rollback()
        except Exception:
            logger.exception("Rollback failed")
            raise
```

## Usage in services

```python
async def create(self, data: ..., family_id: str, user_id: str) -> Model:
    async with self.uow:
        # validation
        await self._validate_something(data.field, family_id)

        model = Model(...)
        created = await self.uow.expenses.create(model)

        # compose with another service via same uow
        await self.installments.generate(created.id, ...)

        return created
```

## Adding a new repository to UoW

1. Add property to `IUnitOfWork` interface
2. Add property + lazy-init to `SQLAlchemyUnitOfWork` implementation
3. No other code changes needed — all services get it automatically
