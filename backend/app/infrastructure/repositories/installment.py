from typing import List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.installment import InstallmentRepository
from app.models import Installment, InstallmentStatus, Expense
from app.core.exceptions import AppException


class SQLAlchemyInstallmentRepository(InstallmentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _active_filter(self):
        return Installment.deleted_at.is_(None)

    async def get_by_expense(self, expense_id: str) -> List[Installment]:
        logger.debug(f"Querying installments for expense: {expense_id}")
        try:
            result = await self.db.execute(
                select(Installment)
                .where(Installment.expense_id == expense_id, self._active_filter())
                .order_by(Installment.installment_number)
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            logger.exception(f"Database error fetching installments for expense {expense_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch installments.")

    async def get_overdue_by_family(self, family_id: str) -> List[Installment]:
        logger.debug(f"Querying overdue installments for family={family_id}")
        try:
            result = await self.db.execute(
                select(Installment)
                .join(Expense)
                .where(
                    and_(
                        Expense.family_id == family_id,
                        Installment.due_date < datetime.utcnow(),
                        Installment.status == InstallmentStatus.PENDING,
                        self._active_filter(),
                    )
                )
                .options(selectinload(Installment.expense))
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            logger.exception(f"Database error fetching overdue installments for family {family_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch overdue installments.")

    async def create(self, installment: Installment) -> Installment:
        logger.debug(f"Persisting installment: expense={installment.expense_id}, #{installment.installment_number}")
        try:
            self.db.add(installment)
            await self.db.flush()
            await self.db.refresh(installment)
            return installment
        except SQLAlchemyError:
            logger.exception("Database error creating installment")
            raise AppException("ERR_DATABASE", "Failed to create installment.")

    async def create_many(self, installments: List[Installment]) -> None:
        logger.debug(f"Persisting {len(installments)} installments")
        try:
            for installment in installments:
                self.db.add(installment)
            await self.db.flush()
        except SQLAlchemyError:
            logger.exception("Database error creating installments in batch")
            raise AppException("ERR_DATABASE", "Failed to create installments.")
