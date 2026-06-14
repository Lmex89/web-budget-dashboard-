"""Expense CRUD service.

SRP: Single responsibility for expense lifecycle (create, read, update, delete).
     Delegates installment generation to InstallmentService.
OCP: Open for extension via dependency injection of IUnitOfWork.
DIP: Depends on IUnitOfWork abstraction, not concrete repositories.
"""
from datetime import datetime
from typing import List, Optional

from loguru import logger

from app.domains.repositories.unit_of_work import IUnitOfWork
from app.domains.services.installment_service import InstallmentService
from app.models import Expense, PaymentMethod
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.core.exceptions import (
    ExpenseNotFoundException,
    ExpenseNotInFamilyException,
    InvalidCategoryForExpenseException,
    InvalidCreditCardForExpenseException,
    InstallmentMisconfigurationException,
)


class ExpenseService:
    """Manages the full lifecycle of expense entities."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow
        self._installment_service: InstallmentService | None = None

    @property
    def installments(self) -> InstallmentService:
        if self._installment_service is None:
            self._installment_service = InstallmentService(self.uow)
        return self._installment_service

    async def get_by_id(self, expense_id: str, family_id: str) -> Expense:
        """Fetch a single expense scoped to the given family."""
        logger.debug(f"Fetching expense: id={expense_id}, family={family_id}")
        async with self.uow:
            expense = await self.uow.expenses.get_by_id(expense_id)
            if not expense:
                logger.warning(f"Expense not found: id={expense_id}")
                raise ExpenseNotFoundException(expense_id)
            if expense.family_id != family_id:
                logger.warning(
                    f"Family mismatch: expense={expense_id} belongs to "
                    f"family={expense.family_id}, requested by family={family_id}"
                )
                raise ExpenseNotInFamilyException()
            return expense

    async def list_by_family(
        self,
        family_id: str,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[List[Expense], int]:
        """Paginated list of expenses for the given family."""
        logger.info(f"Listing expenses: family={family_id}, page={page}, size={page_size}")
        async with self.uow:
            return await self.uow.expenses.get_by_family(
                family_id, page, page_size, category_id, start_date, end_date,
            )

    async def create(self, data: ExpenseCreate, family_id: str, user_id: str) -> Expense:
        """Create a new expense with family-scoped validation."""
        logger.info(
            f"Creating expense: amount={data.amount}, method={data.payment_method}, "
            f"category={data.category_id}, user={user_id}"
        )
        async with self.uow:
            await self._validate_category(data.category_id, family_id)
            await self._validate_credit_card(data.payment_method, data.credit_card_id, family_id)
            self._validate_installment_config(data)

            expense = Expense(
                amount=data.amount,
                description=data.description,
                date=data.date,
                payment_method=data.payment_method,
                is_installment=data.is_installment,
                total_installments=data.total_installments,
                installment_number=1 if data.is_installment else None,
                family_id=family_id,
                user_id=user_id,
                category_id=data.category_id,
                credit_card_id=data.credit_card_id,
            )

            created = await self.uow.expenses.create(expense)

            if data.is_installment and data.total_installments:
                await self.installments.generate(created.id, data.total_installments, data.amount)

            return created

    async def update(self, expense_id: str, data: ExpenseUpdate, family_id: str) -> Expense:
        """Partially update an expense."""
        logger.info(f"Updating expense: id={expense_id}")
        async with self.uow:
            expense = await self.get_by_id(expense_id, family_id)
            update_data = data.model_dump(exclude_unset=True)
            logger.debug(f"Updating fields for expense={expense_id}: {list(update_data.keys())}")

            for field, value in update_data.items():
                setattr(expense, field, value)

            expense.updated_at = datetime.utcnow()
            return await self.uow.expenses.update(expense)

    async def delete(self, expense_id: str, family_id: str) -> bool:
        """Soft-delete or hard-delete an expense (currently hard-delete)."""
        logger.warning(f"Deleting expense: id={expense_id}, family={family_id}")
        async with self.uow:
            await self.get_by_id(expense_id, family_id)
            return await self.uow.expenses.delete(expense_id)

    # ── Private validators (single responsibility per check) ──

    async def _validate_category(self, category_id: str, family_id: str) -> None:
        category = await self.uow.categories.get_by_id(category_id)
        if not category or category.family_id != family_id:
            logger.warning(f"Invalid category for expense: id={category_id}, family={family_id}")
            raise InvalidCategoryForExpenseException(category_id)

    async def _validate_credit_card(
        self,
        payment_method: PaymentMethod,
        credit_card_id: str | None,
        family_id: str,
    ) -> None:
        if payment_method != PaymentMethod.CREDIT:
            return
        if not credit_card_id:
            raise InstallmentMisconfigurationException("Credit card is required for credit payments.")
        card = await self.uow.credit_cards.get_by_id(credit_card_id)
        if not card or card.family_id != family_id:
            logger.warning(f"Invalid credit card for expense: id={credit_card_id}")
            raise InvalidCreditCardForExpenseException(credit_card_id)

    @staticmethod
    def _validate_installment_config(data: ExpenseCreate) -> None:
        if data.is_installment and data.payment_method != PaymentMethod.CREDIT:
            raise InstallmentMisconfigurationException(
                "Installments require credit card payment method."
            )
