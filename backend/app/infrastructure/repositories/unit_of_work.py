from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.infrastructure.repositories.expense import SQLAlchemyExpenseRepository
from app.infrastructure.repositories.category import SQLAlchemyCategoryRepository
from app.infrastructure.repositories.credit_card import SQLAlchemyCreditCardRepository
from app.infrastructure.repositories.debt import SQLAlchemyDebtRepository
from app.infrastructure.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.repositories.audit_log import SQLAlchemyAuditLogRepository


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._expenses = None
        self._categories = None
        self._credit_cards = None
        self._debts = None
        self._users = None
        self._audit_logs = None

    @property
    def expenses(self):
        if self._expenses is None:
            self._expenses = SQLAlchemyExpenseRepository(self._session)
        return self._expenses

    @property
    def categories(self):
        if self._categories is None:
            self._categories = SQLAlchemyCategoryRepository(self._session)
        return self._categories

    @property
    def credit_cards(self):
        if self._credit_cards is None:
            self._credit_cards = SQLAlchemyCreditCardRepository(self._session)
        return self._credit_cards

    @property
    def debts(self):
        if self._debts is None:
            self._debts = SQLAlchemyDebtRepository(self._session)
        return self._debts

    @property
    def users(self):
        if self._users is None:
            self._users = SQLAlchemyUserRepository(self._session)
        return self._users

    @property
    def audit_logs(self):
        if self._audit_logs is None:
            self._audit_logs = SQLAlchemyAuditLogRepository(self._session)
        return self._audit_logs

    async def __aenter__(self) -> Self:
        logger.debug("Unit of Work started (transaction begin)")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            logger.warning(f"UoW exiting with exception: {exc_type.__name__}: {exc_val}")
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    async def commit(self) -> None:
        logger.debug("Committing transaction")
        try:
            await self._session.commit()
            logger.debug("Transaction committed successfully")
        except Exception:
            logger.exception("Commit failed")
            raise

    async def rollback(self) -> None:
        logger.warning("Rolling back transaction")
        try:
            await self._session.rollback()
            logger.debug("Transaction rolled back")
        except Exception:
            logger.exception("Rollback failed")
            raise

    async def close(self) -> None:
        logger.debug("Closing database session")
        try:
            await self._session.close()
            logger.debug("Session closed")
        except Exception:
            logger.exception("Session close failed")
            raise
