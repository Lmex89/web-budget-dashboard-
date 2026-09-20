from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.budget import BudgetRepository
from app.models import Budget, BudgetCategory
from app.core.exceptions import NotFoundException, AppException


class SQLAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _active_filter(self):
        return Budget.deleted_at.is_(None)

    def _active_category_filter(self):
        return BudgetCategory.deleted_at.is_(None)

    def _with_active_categories(self):
        return with_loader_criteria(BudgetCategory, BudgetCategory.deleted_at.is_(None))

    async def get_by_id(self, budget_id: str) -> Optional[Budget]:
        logger.debug(f"Querying budget by id: {budget_id}")
        try:
            result = await self.db.execute(
                select(Budget)
                .where(Budget.id == budget_id, self._active_filter())
                .options(self._with_active_categories())
                .execution_options(populate_existing=True)
            )
            budget = result.scalar_one_or_none()
            logger.debug(f"Budget {'found' if budget else 'not found'}: id={budget_id}")
            return budget
        except SQLAlchemyError:
            logger.exception(f"Database error fetching budget {budget_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch budget.")

    async def get_by_period(
        self,
        family_id: str,
        year: int,
        month: int,
        include_deleted: bool = False,
    ) -> Optional[Budget]:
        logger.debug(f"Querying budget: family={family_id}, period={year}-{month:02d}")
        try:
            conditions = [
                Budget.family_id == family_id,
                Budget.year == year,
                Budget.month == month,
            ]
            if not include_deleted:
                conditions.append(self._active_filter())
            result = await self.db.execute(
                select(Budget)
                .where(*conditions)
                .options(self._with_active_categories())
                .limit(1)
                .execution_options(populate_existing=True)
            )
            budget = result.scalar_one_or_none()
            logger.debug(f"Budget {'found' if budget else 'not found'}: {year}-{month:02d}")
            return budget
        except SQLAlchemyError:
            logger.exception("Database error fetching budget by period")
            raise AppException("ERR_DATABASE", "Failed to fetch budget.")

    async def list_by_family(self, family_id: str, year: Optional[int] = None) -> List[Budget]:
        logger.debug(f"Listing budgets: family={family_id}, year={year}")
        try:
            conditions = [Budget.family_id == family_id, self._active_filter()]
            if year:
                conditions.append(Budget.year == year)
            result = await self.db.execute(
                select(Budget)
                .where(*conditions)
                .options(self._with_active_categories())
                .order_by(desc(Budget.year), desc(Budget.month))
            )
            budgets = list(result.scalars().unique().all())
            logger.debug(f"Returning {len(budgets)} budgets")
            return budgets
        except SQLAlchemyError:
            logger.exception("Database error listing budgets")
            raise AppException("ERR_DATABASE", "Failed to list budgets.")

    async def create(self, budget: Budget) -> Budget:
        logger.debug(f"Persisting new budget: period={budget.year}-{budget.month:02d}")
        try:
            self.db.add(budget)
            await self.db.flush()
            await self.db.refresh(budget)
            logger.debug(f"Budget persisted: id={budget.id}")
            return budget
        except SQLAlchemyError:
            logger.exception("Database error creating budget")
            raise AppException("ERR_DATABASE", "Failed to create budget.")

    async def update(self, budget: Budget) -> Budget:
        logger.debug(f"Updating budget: id={budget.id}")
        try:
            await self.db.flush()
            await self.db.refresh(budget)
            logger.debug(f"Budget updated: id={budget.id}")
            return budget
        except SQLAlchemyError:
            logger.exception(f"Database error updating budget {budget.id}")
            raise AppException("ERR_DATABASE", "Failed to update budget.")

    async def delete(self, budget_id: str) -> bool:
        logger.warning(f"Soft-deleting budget: id={budget_id}")
        try:
            budget = await self.get_by_id(budget_id)
            if not budget:
                raise NotFoundException("Budget", budget_id)
            now = datetime.utcnow()
            budget.deleted_at = now
            for entry in budget.categories:
                entry.deleted_at = now
            await self.db.flush()
            logger.info(f"Budget soft-deleted: id={budget_id}")
            return True
        except NotFoundException:
            raise
        except SQLAlchemyError:
            logger.exception(f"Database error soft-deleting budget {budget_id}")
            raise AppException("ERR_DATABASE", "Failed to delete budget.")

    async def add_category(self, entry: BudgetCategory) -> BudgetCategory:
        logger.debug(
            f"Persisting budget category: budget={entry.budget_id}, category={entry.category_id}"
        )
        try:
            self.db.add(entry)
            await self.db.flush()
            await self.db.refresh(entry)
            return entry
        except SQLAlchemyError:
            logger.exception("Database error creating budget category")
            raise AppException("ERR_DATABASE", "Failed to create budget category.")

    async def get_category_entry(
        self,
        budget_id: str,
        category_id: str,
        include_deleted: bool = False,
    ) -> Optional[BudgetCategory]:
        logger.debug(f"Querying budget category: budget={budget_id}, category={category_id}")
        try:
            conditions = [
                BudgetCategory.budget_id == budget_id,
                BudgetCategory.category_id == category_id,
            ]
            if not include_deleted:
                conditions.append(self._active_category_filter())
            result = await self.db.execute(
                select(BudgetCategory).where(*conditions).limit(1)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            logger.exception("Database error fetching budget category")
            raise AppException("ERR_DATABASE", "Failed to fetch budget category.")

    async def delete_category(self, entry: BudgetCategory) -> bool:
        logger.debug(f"Soft-deleting budget category: id={entry.id}")
        try:
            entry.deleted_at = datetime.utcnow()
            await self.db.flush()
            return True
        except SQLAlchemyError:
            logger.exception(f"Database error soft-deleting budget category {entry.id}")
            raise AppException("ERR_DATABASE", "Failed to delete budget category.")
