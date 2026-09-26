from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, func, and_, desc, extract
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

    def _active_filter(self):
        return Expense.deleted_at.is_(None)

    @staticmethod
    def _category_filter(category_id: Optional[str]) -> Optional[List[str]]:
        if not category_id:
            return None
        ids = [c.strip() for c in category_id.split(",") if c.strip()]
        return ids if ids else None

    @staticmethod
    def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        return start, end

    async def get_by_id(self, expense_id: str) -> Optional[Expense]:
        logger.debug(f"Querying expense by id: {expense_id}")
        try:
            result = await self.db.execute(
                select(Expense)
                .where(Expense.id == expense_id, self._active_filter())
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
        page_size: int = 25,
        category_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        credit_card_id: Optional[str] = None,
    ) -> tuple[List[Expense], int]:
        conditions = [Expense.family_id == family_id, self._active_filter()]

        category_ids = self._category_filter(category_id)
        if category_ids:
            if len(category_ids) == 1:
                conditions.append(Expense.category_id == category_ids[0])
            else:
                conditions.append(Expense.category_id.in_(category_ids))
            logger.debug(f"Filtering by category ids: {category_ids}")
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

    async def get_by_family_csv(
        self,
        family_id: str,
        category_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Expense]:
        conditions = [Expense.family_id == family_id, self._active_filter()]
        category_ids = self._category_filter(category_id)
        if category_ids:
            if len(category_ids) == 1:
                conditions.append(Expense.category_id == category_ids[0])
            else:
                conditions.append(Expense.category_id.in_(category_ids))
        if start_date:
            conditions.append(Expense.date >= datetime.fromisoformat(start_date))
        if end_date:
            conditions.append(Expense.date <= datetime.fromisoformat(end_date))
        try:
            stmt = (
                select(Expense)
                .where(and_(*conditions))
                .options(
                    joinedload(Expense.category),
                    joinedload(Expense.user),
                    joinedload(Expense.credit_card),
                )
                .order_by(desc(Expense.date))
            )
            result = await self.db.execute(stmt)
            expenses = result.scalars().unique().all()
            return list(expenses)
        except SQLAlchemyError:
            logger.exception("Database error exporting expenses")
            raise AppException("ERR_DATABASE", "Failed to export expenses.")

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
        logger.warning(f"Soft-deleting expense: id={expense_id}")
        try:
            expense = await self.get_by_id(expense_id)
            if not expense:
                raise NotFoundException("Expense", expense_id)
            expense.deleted_at = datetime.utcnow()
            await self.db.flush()
            logger.info(f"Expense soft-deleted: id={expense_id}")
            return True
        except NotFoundException:
            raise
        except SQLAlchemyError:
            logger.exception(f"Database error soft-deleting expense {expense_id}")
            raise AppException("ERR_DATABASE", "Failed to delete expense.")

    async def get_family_monthly_summary(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> dict:
        logger.debug(f"Aggregating monthly summary: family={family_id}, {year}-{month:02d}")
        try:
            month_start, next_month_start = self._month_bounds(year, month)
            conditions = [
                Expense.family_id == family_id,
                self._active_filter(),
                Expense.date >= month_start,
                Expense.date < next_month_start,
            ]
            if category_id:
                conditions.append(Expense.category_id == category_id)
            stmt = select(
                func.coalesce(func.sum(Expense.amount), 0).label("total")
            ).where(and_(*conditions))
            result = await self.db.execute(stmt)
            total = result.scalar()
            logger.debug(f"Monthly total for {year}-{month:02d}: {total}")
            return {"total_expenses": total, "year": year, "month": month}
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
        try:
            month_start, next_month_start = self._month_bounds(year, month)
            conditions = [
                Expense.family_id == family_id,
                self._active_filter(),
                Expense.date >= month_start,
                Expense.date < next_month_start,
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
                {"category": row.name, "color": row.color, "amount": row.total}
                for row in rows
            ]
        except SQLAlchemyError:
            logger.exception("Database error aggregating categories")
            raise AppException("ERR_DATABASE", "Failed to compute category distribution.")

    async def get_category_spending(
        self,
        family_id: str,
        year: int,
        month: int,
    ) -> List[dict]:
        logger.debug(f"Aggregating category spending: family={family_id}, {year}-{month:02d}")
        try:
            month_start, next_month_start = self._month_bounds(year, month)
            conditions = [
                Expense.family_id == family_id,
                self._active_filter(),
                Expense.date >= month_start,
                Expense.date < next_month_start,
            ]
            stmt = (
                select(
                    Category.id,
                    Category.name,
                    Category.color,
                    func.coalesce(func.sum(Expense.amount), 0).label("total"),
                )
                .join(Expense, Expense.category_id == Category.id)
                .where(and_(*conditions))
                .group_by(Category.id, Category.name, Category.color)
                .order_by(desc("total"))
            )
            result = await self.db.execute(stmt)
            rows = result.all()
            logger.debug(f"Category spending has {len(rows)} categories")
            return [
                {
                    "category_id": row.id,
                    "category": row.name,
                    "color": row.color,
                    "amount": row.total,
                }
                for row in rows
            ]
        except SQLAlchemyError:
            logger.exception("Database error aggregating category spending")
            raise AppException("ERR_DATABASE", "Failed to compute category spending.")

    async def get_monthly_spending_with_total(
        self,
        family_id: str,
        year: int,
        month: int,
    ) -> dict:
        logger.debug(f"Aggregating monthly spending with total: family={family_id}, {year}-{month:02d}")
        try:
            month_start, next_month_start = self._month_bounds(year, month)
            conditions = [
                Expense.family_id == family_id,
                self._active_filter(),
                Expense.date >= month_start,
                Expense.date < next_month_start,
            ]
            stmt = (
                select(
                    Category.id.label("category_id"),
                    Category.name,
                    Category.color,
                    func.coalesce(func.sum(Expense.amount), 0).label("category_total"),
                    func.coalesce(func.sum(func.sum(Expense.amount)).over(), 0).label("grand_total"),
                )
                .join(Expense, Expense.category_id == Category.id)
                .where(and_(*conditions))
                .group_by(Category.id, Category.name, Category.color)
                .order_by(desc("category_total"))
            )
            result = await self.db.execute(stmt)
            rows = result.all()
            logger.debug(f"Monthly spending has {len(rows)} categories")

            total_expenses = rows[0].grand_total if rows else Decimal("0")
            category_spending = [
                {
                    "category_id": row.category_id,
                    "category": row.name,
                    "color": row.color,
                    "amount": row.category_total,
                }
                for row in rows
            ]
            return {
                "total_expenses": total_expenses,
                "year": year,
                "month": month,
                "category_spending": category_spending,
            }
        except SQLAlchemyError:
            logger.exception("Database error aggregating monthly spending with total")
            raise AppException("ERR_DATABASE", "Failed to compute monthly spending.")

    async def get_monthly_trend(self, family_id: str, year: int) -> List[dict]:
        logger.debug(f"Aggregating monthly trend: family={family_id}, year={year}")
        try:
            month_expr = extract("month", Expense.date)
            stmt = (
                select(
                    month_expr.label("month"),
                    func.coalesce(func.sum(Expense.amount), 0).label("total"),
                )
                .where(
                    and_(
                        Expense.family_id == family_id,
                        self._active_filter(),
                        Expense.date >= datetime(year, 1, 1),
                        Expense.date < datetime(year + 1, 1, 1),
                    )
                )
                .group_by(month_expr)
            )
            result = await self.db.execute(stmt)
            totals = {int(row.month): row.total for row in result.all()}
            logger.debug(f"Monthly trend for {year} has {len(totals)} active months")
            return [
                {"year": year, "month": month, "total_expenses": totals.get(month, Decimal("0"))}
                for month in range(1, 13)
            ]
        except SQLAlchemyError:
            logger.exception("Database error aggregating monthly trend")
            raise AppException("ERR_DATABASE", "Failed to compute monthly trend.")
