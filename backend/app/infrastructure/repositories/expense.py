from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.expense import ExpenseRepository
from app.models import Expense, Category
from app.core.exceptions import NotFoundException, AppException

class SQLAlchemyExpenseRepository(ExpenseRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, expense_id: str) -> Optional[Expense]:
        logger.debug(f"Querying expense by id: {expense_id}")
        try:
            result = await self.db.execute(
                select(Expense)
                .where(Expense.id == expense_id)
                .options(
                    selectinload(Expense.category),
                    selectinload(Expense.user),
                    selectinload(Expense.credit_card),
                    selectinload(Expense.installments),
                )
            )
            expense = result.scalar_one_or_none()
            if expense:
                logger.debug(f"Expense found: id={expense_id}")
            else:
                logger.debug(f"Expense not found: id={expense_id}")
            return expense
        except SQLAlchemyError:
            logger.exception(f"Database error fetching expense {expense_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch expense.")


    async def get_by_family(
        self,
        family_id: str,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        credit_card_id: Optional[str] = None,
    ) -> tuple[List[Expense], int]:
        conditions = [Expense.family_id == family_id]

        if category_id:
            conditions.append(Expense.category_id == category_id)
            logger.debug(f"Filtering by category: {category_id}")
        if start_date:
            conditions.append(Expense.date >= datetime.fromisoformat(start_date))
            logger.debug(f"Filtering from date: {start_date}")
        if end_date:
            conditions.append(Expense.date <= datetime.fromisoformat(end_date))
            logger.debug(f"Filtering to date: {end_date}")
        if credit_card_id:
            conditions.append(Expense.credit_card_id == credit_card_id)
            logger.debug(f"Filtering by credit card: {credit_card_id}")

        try:
            count_stmt = select(func.count()).select_from(Expense).where(and_(*conditions))
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar()
            logger.debug(f"Total expenses matching filter: {total}")

            stmt = (
                select(Expense)
                .where(and_(*conditions))
                .options(
                    joinedload(Expense.category),
                    joinedload(Expense.user),
                    joinedload(Expense.credit_card),
                )
                .order_by(desc(Expense.date))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )

            result = await self.db.execute(stmt)
            expenses = result.scalars().unique().all()
            logger.debug(f"Returning {len(expenses)} expenses (page {page}/{(total + page_size - 1) // page_size})")
            return list(expenses), total
        except SQLAlchemyError:
            logger.exception("Database error listing expenses")
            raise AppException("ERR_DATABASE", "Failed to list expenses.")

    async def create(self, expense: Expense) -> Expense:
        logger.debug(f"Persisting new expense: amount={expense.amount}, date={expense.date}")
        try:
            self.db.add(expense)
            await self.db.flush()
            await self.db.refresh(expense)
            logger.debug(f"Expense persisted: id={expense.id}")
            return expense
        except SQLAlchemyError:
            logger.exception("Database error creating expense")
            raise AppException("ERR_DATABASE", "Failed to create expense.")

    async def update(self, expense: Expense) -> Expense:
        logger.debug(f"Updating expense: id={expense.id}")
        try:
            await self.db.flush()
            await self.db.refresh(expense)
            logger.debug(f"Expense updated: id={expense.id}")
            return expense
        except SQLAlchemyError:
            logger.exception(f"Database error updating expense {expense.id}")
            raise AppException("ERR_DATABASE", "Failed to update expense.")

    async def delete(self, expense_id: str) -> bool:
        logger.debug(f"Removing expense: id={expense_id}")
        try:
            expense = await self.get_by_id(expense_id)
            if not expense:
                raise NotFoundException("Expense", expense_id)
            await self.db.delete(expense)
            await self.db.flush()
            logger.info(f"Expense removed: id={expense_id}")
            return True
        except NotFoundException:
            raise
        except SQLAlchemyError:
            logger.exception(f"Database error deleting expense {expense_id}")
            raise AppException("ERR_DATABASE", "Failed to delete expense.")

    async def get_family_monthly_summary(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> dict:
        logger.debug(f"Aggregating monthly summary: family={family_id}, {year}-{month:02d}")
        from sqlalchemy import extract
        try:
            conditions = [
                Expense.family_id == family_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month,
            ]
            if category_id:
                conditions.append(Expense.category_id == category_id)
            stmt = select(
                func.coalesce(func.sum(Expense.amount), 0).label("total")
            ).where(and_(*conditions))
            result = await self.db.execute(stmt)
            total = result.scalar()
            logger.debug(f"Monthly total for {year}-{month:02d}: {total}")
            return {"total_expenses": float(total), "year": year, "month": month}
        except SQLAlchemyError:
            logger.exception("Database error aggregating monthly summary")
            raise AppException("ERR_DATABASE", "Failed to compute monthly summary.")

    async def get_category_distribution(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> List[dict]:
        logger.debug(f"Aggregating category distribution: family={family_id}, {year}-{month:02d}")
        from sqlalchemy import extract
        try:
            conditions = [
                Expense.family_id == family_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month,
            ]
            if category_id:
                conditions.append(Expense.category_id == category_id)
            stmt = (
                select(
                    Category.name,
                    Category.color,
                    func.coalesce(func.sum(Expense.amount), 0).label("total"),
                )
                .join(Expense, Expense.category_id == Category.id)
                .where(and_(*conditions))
                .group_by(Category.id)
                .order_by(desc("total"))
            )
            result = await self.db.execute(stmt)
            rows = result.all()
            logger.debug(f"Category distribution has {len(rows)} categories")
            return [
                {"category": row.name, "color": row.color, "amount": float(row.total)}
                for row in rows
            ]
        except SQLAlchemyError:
            logger.exception("Database error aggregating categories")
            raise AppException("ERR_DATABASE", "Failed to compute category distribution.")
