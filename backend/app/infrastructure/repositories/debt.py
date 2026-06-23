from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.debt import DebtRepository
from app.models import Debt, DebtStatus
from app.core.exceptions import NotFoundException, AppException


class SQLAlchemyDebtRepository(DebtRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _active_filter(self):
        return Debt.deleted_at.is_(None)

    async def get_by_id(self, debt_id: str) -> Optional[Debt]:
        logger.debug(f"Querying debt by id: {debt_id}")
        try:
            result = await self.db.execute(
                select(Debt).where(Debt.id == debt_id, self._active_filter())
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            logger.exception(f"Database error fetching debt {debt_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch debt.")

    async def get_by_family(self, family_id: str) -> List[Debt]:
        logger.debug(f"Querying debts for family: {family_id}")
        try:
            result = await self.db.execute(
                select(Debt)
                .where(Debt.family_id == family_id, self._active_filter())
                .options(selectinload(Debt.expenses))
                .order_by(Debt.created_at.desc())
            )
            debts = list(result.scalars().unique().all())
            logger.debug(f"Found {len(debts)} debts for family {family_id}")
            return debts
        except SQLAlchemyError:
            logger.exception("Database error listing debts")
            raise AppException("ERR_DATABASE", "Failed to list debts.")

    async def create(self, debt: Debt) -> Debt:
        logger.info(f"Creating debt: name={debt.name}, amount={debt.original_amount}, type={debt.type}")
        try:
            self.db.add(debt)
            await self.db.flush()
            await self.db.refresh(debt)
            logger.info(f"Debt created: id={debt.id}, name={debt.name}")
            return debt
        except SQLAlchemyError:
            logger.exception("Database error creating debt")
            raise AppException("ERR_DATABASE", "Failed to create debt.")

    async def update(self, debt: Debt) -> Debt:
        logger.info(f"Updating debt: id={debt.id}")
        try:
            await self.db.flush()
            await self.db.refresh(debt)
            return debt
        except SQLAlchemyError:
            logger.exception(f"Database error updating debt {debt.id}")
            raise AppException("ERR_DATABASE", "Failed to update debt.")

    async def delete(self, debt_id: str) -> bool:
        logger.warning(f"Soft-deleting debt: id={debt_id}")
        try:
            debt = await self.get_by_id(debt_id)
            if not debt:
                raise NotFoundException("Debt", debt_id)
            debt.deleted_at = datetime.utcnow()
            await self.db.flush()
            return True
        except NotFoundException:
            raise
        except SQLAlchemyError:
            logger.exception(f"Database error soft-deleting debt {debt_id}")
            raise AppException("ERR_DATABASE", "Failed to delete debt.")

    async def update_remaining_amount(self, debt_id: str, new_amount: float) -> Debt:
        logger.info(f"Updating remaining amount: debt={debt_id}, new_amount={new_amount}")
        try:
            debt = await self.get_by_id(debt_id)
            if not debt:
                raise NotFoundException("Debt", debt_id)
            debt.remaining_amount = new_amount
            if new_amount <= 0:
                debt.status = DebtStatus.PAID
                logger.info(f"Debt {debt_id} fully paid, marking as PAID")
            await self.db.flush()
            await self.db.refresh(debt)
            return debt
        except NotFoundException:
            raise
        except SQLAlchemyError:
            logger.exception(f"Database error updating debt amount {debt_id}")
            raise AppException("ERR_DATABASE", "Failed to update debt amount.")
