from abc import ABC, abstractmethod
from typing import Self

from app.domains.repositories.expense import ExpenseRepository
from app.domains.repositories.category import CategoryRepository
from app.domains.repositories.credit_card import CreditCardRepository
from app.domains.repositories.debt import DebtRepository
from app.domains.repositories.user import UserRepository
from app.domains.repositories.audit_log import AuditLogRepository


class IUnitOfWork(ABC):
    expenses: ExpenseRepository
    categories: CategoryRepository
    credit_cards: CreditCardRepository
    debts: DebtRepository
    users: UserRepository
    audit_logs: AuditLogRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass
