"""Budget service.

SRP: Single responsibility for monthly budget lifecycle and budget-vs-actual
     progress computation.
OCP: Open for extension with new progress metrics without modifying CRUD.
DIP: Depends on IUnitOfWork abstraction, not concrete repositories.
"""
import uuid
from decimal import Decimal
from typing import List, Optional

from loguru import logger

from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import Budget, BudgetCategory, AuditLog
from app.schemas.budget import BudgetUpsert
from app.core.exceptions import (
    BudgetNotFoundException,
    BudgetNotInFamilyException,
    InvalidCategoryForBudgetException,
    InvalidBudgetPeriodException,
)

STATUS_ON_TRACK = "on_track"
STATUS_WARNING = "warning"
STATUS_OVER = "over"
WARNING_THRESHOLD = 0.8


class BudgetService:
    """Manages monthly budgets and computes progress against real spending."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def get_by_id(self, budget_id: str, family_id: str) -> Budget:
        """Fetch a single budget scoped to the given family."""
        logger.debug(f"Fetching budget: id={budget_id}, family={family_id}")
        budget = await self.uow.budgets.get_by_id(budget_id)
        if not budget:
            logger.warning(f"Budget not found: id={budget_id}")
            raise BudgetNotFoundException(budget_id)
        if budget.family_id != family_id:
            logger.warning(
                f"Family mismatch: budget={budget_id} belongs to "
                f"family={budget.family_id}, requested by family={family_id}"
            )
            raise BudgetNotInFamilyException(budget_id)
        return budget

    async def list_by_family(self, family_id: str, year: Optional[int] = None) -> List[Budget]:
        """List budgets for the given family, optionally filtered by year."""
        logger.info(f"Listing budgets: family={family_id}, year={year}")
        async with self.uow:
            return await self.uow.budgets.list_by_family(family_id, year)

    async def get_progress(self, family_id: str, year: int, month: int) -> Optional[dict]:
        """Budget-vs-actual progress for a period, or None when no budget exists."""
        self._validate_period(year, month)
        logger.info(f"Computing budget progress: family={family_id}, period={year}-{month:02d}")
        async with self.uow:
            budget = await self.uow.budgets.get_by_period(family_id, year, month)
            if not budget:
                logger.debug(f"No budget set for {year}-{month:02d}")
                return None
            return await self._build_progress(budget, family_id, year, month)

    async def upsert(
        self,
        family_id: str,
        user_id: str,
        year: int,
        month: int,
        data: BudgetUpsert,
    ) -> Budget:
        """Create or replace the budget (and category limits) for a period."""
        self._validate_period(year, month)
        logger.info(
            f"Upserting budget: family={family_id}, period={year}-{month:02d}, "
            f"total={data.total_budget}, categories={len(data.categories)}"
        )
        async with self.uow:
            budget = await self.uow.budgets.get_by_period(
                family_id, year, month, include_deleted=True
            )

            if budget and budget.deleted_at is not None:
                logger.info(f"Restoring soft-deleted budget: id={budget.id}, period={year}-{month:02d}")
                old_values = self._serialize_budget(budget)
                budget.deleted_at = None
                budget.total_budget = data.total_budget
                await self._sync_categories(budget, data.categories, family_id)
                await self.uow.budgets.update(budget)
                await self._audit(user_id, "update", budget.id, old_values, self._serialize_budget(budget))
            elif budget:
                old_values = self._serialize_budget(budget)
                budget.total_budget = data.total_budget
                await self._sync_categories(budget, data.categories, family_id)
                await self.uow.budgets.update(budget)
                await self._audit(user_id, "update", budget.id, old_values, self._serialize_budget(budget))
            else:
                budget = Budget(
                    id=str(uuid.uuid4()),
                    family_id=family_id,
                    year=year,
                    month=month,
                    total_budget=data.total_budget,
                )
                budget = await self.uow.budgets.create(budget)
                await self._sync_categories(budget, data.categories, family_id)
                await self._audit(user_id, "create", budget.id, None, self._serialize_budget(budget))

            refreshed = await self.uow.budgets.get_by_period(family_id, year, month)
            return refreshed or budget

    async def delete(self, budget_id: str, family_id: str, user_id: str) -> bool:
        """Soft-delete a budget and its category limits."""
        logger.warning(f"Deleting budget: id={budget_id}, family={family_id}")
        async with self.uow:
            budget = await self.get_by_id(budget_id, family_id)
            await self._audit(user_id, "delete", budget.id, self._serialize_budget(budget), None)
            return await self.uow.budgets.delete(budget_id)

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _validate_period(year: int, month: int) -> None:
        if year < 2020 or year > 2100:
            raise InvalidBudgetPeriodException(f"Year '{year}' is out of range (2020-2100).")
        if month < 1 or month > 12:
            raise InvalidBudgetPeriodException(f"Month '{month}' must be between 1 and 12.")

    async def _validate_category(self, category_id: str, family_id: str) -> None:
        category = await self.uow.categories.get_by_id(category_id)
        if not category or category.family_id != family_id:
            logger.warning(f"Invalid category for budget: id={category_id}, family={family_id}")
            raise InvalidCategoryForBudgetException(category_id)

    async def _sync_categories(
        self,
        budget: Budget,
        items: List,
        family_id: str,
    ) -> None:
        """Reconcile incoming category limits with the persisted entries."""
        incoming = {item.category_id: item.amount for item in items}
        existing = {entry.category_id: entry for entry in budget.categories}

        for category_id, amount in incoming.items():
            await self._validate_category(category_id, family_id)
            entry = existing.get(category_id)
            if entry:
                entry.amount = amount
                continue
            stale = await self.uow.budgets.get_category_entry(
                budget.id, category_id, include_deleted=True
            )
            if stale:
                stale.deleted_at = None
                stale.amount = amount
                logger.debug(f"Restored budget category: budget={budget.id}, category={category_id}")
            else:
                await self.uow.budgets.add_category(
                    BudgetCategory(
                        id=str(uuid.uuid4()),
                        budget_id=budget.id,
                        category_id=category_id,
                        amount=amount,
                    )
                )

        for category_id, entry in existing.items():
            if category_id not in incoming:
                await self.uow.budgets.delete_category(entry)

    async def _build_progress(
        self,
        budget: Budget,
        family_id: str,
        year: int,
        month: int,
    ) -> dict:
        spending_data = await self.uow.expenses.get_monthly_spending_with_total(family_id, year, month)
        total_spent = spending_data["total_expenses"] or Decimal("0")
        spending = {row["category_id"]: row["amount"] for row in spending_data["category_spending"]}

        categories = []
        budgeted_ids = set()
        for entry in budget.categories:
            budgeted_ids.add(entry.category_id)
            amount = entry.amount
            spent = spending.get(entry.category_id, Decimal("0"))
            categories.append(
                {
                    "category_id": entry.category_id,
                    "category_name": entry.category.name,
                    "color": entry.category.color,
                    "budget_amount": amount,
                    "spent": spent,
                    "remaining": amount - spent,
                    "percentage": float(spent / amount * 100) if amount > 0 else 0.0,
                    "status": self._status(spent, amount),
                }
            )
        categories.sort(key=lambda c: c["budget_amount"], reverse=True)

        unbudgeted_spent = sum(
            amount for category_id, amount in spending.items() if category_id not in budgeted_ids
        )

        return {
            "budget_id": budget.id,
            "year": year,
            "month": month,
            "total_budget": budget.total_budget,
            "total_spent": total_spent,
            "remaining": budget.total_budget - total_spent,
            "percentage": float(total_spent / budget.total_budget * 100),
            "unbudgeted_spent": unbudgeted_spent,
            "status": self._status(total_spent, budget.total_budget),
            "categories": categories,
        }

    @staticmethod
    def _status(spent: Decimal, limit: Decimal) -> str:
        if limit <= 0:
            return STATUS_ON_TRACK if spent <= 0 else STATUS_OVER
        ratio = float(spent / limit)
        if ratio > 1:
            return STATUS_OVER
        if ratio >= WARNING_THRESHOLD:
            return STATUS_WARNING
        return STATUS_ON_TRACK

    @staticmethod
    def _serialize_budget(budget: Budget) -> dict:
        return {
            "year": budget.year,
            "month": budget.month,
            "total_budget": str(budget.total_budget),
            "categories": [
                {"category_id": entry.category_id, "amount": str(entry.amount)}
                for entry in budget.categories
            ],
        }

    async def _audit(
        self,
        user_id: str,
        action: str,
        entity_id: str,
        old_values: Optional[dict],
        new_values: Optional[dict],
    ) -> None:
        audit = AuditLog(
            id=str(uuid.uuid4()),
            entity_type="budget",
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id,
        )
        await self.uow.audit_logs.create(audit)
