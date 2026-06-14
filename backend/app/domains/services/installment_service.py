"""Installment generation and tracking service.

SRP: Handles only installment lifecycle (generation, status tracking).
     Called by ExpenseService when creating installment-based expenses.
OCP: Extensible via IInstallmentStrategy implementations (e.g., fixed vs. variable amounts).
DIP: Depends on IUnitOfWork abstraction.
"""
from datetime import datetime
from decimal import Decimal

from loguru import logger
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import Installment, InstallmentStatus, Expense


class InstallmentService:
    """Creates and manages installment records for split-payment expenses."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def generate(
        self,
        expense_id: str,
        total_installments: int,
        total_amount: Decimal,
        credit_card_id: str | None = None,
    ) -> list[Installment]:
        """Create installment records for a given expense.

        Each installment is spread evenly across subsequent months.
        """
        logger.info(
            f"Generating {total_installments} installments for expense={expense_id}, "
            f"total={total_amount}"
        )
        base_amount = total_amount / Decimal(total_installments)
        due_date = datetime.utcnow()
        installments: list[Installment] = []

        for i in range(1, total_installments + 1):
            installment = Installment(
                expense_id=expense_id,
                credit_card_id=credit_card_id,
                installment_number=i,
                total_installments=total_installments,
                amount=base_amount,
                due_date=due_date,
                status=InstallmentStatus.PENDING,
            )
            self.uow._session.add(installment)
            installments.append(installment)
            logger.debug(
                f"Installment #{i}/{total_installments} for expense={expense_id}: "
                f"amount={base_amount}, due={due_date}"
            )
            due_date = self._add_months(due_date, 1)

        return installments

    async def get_overdue(self, family_id: str) -> list[Installment]:
        """Return all overdue installments for a family."""
        logger.debug(f"Querying overdue installments for family={family_id}")
        async with self.uow:
            result = await self.uow._session.execute(
                select(Installment)
                .join(Expense)
                .where(
                    and_(
                        Expense.family_id == family_id,
                        Installment.due_date < datetime.utcnow(),
                        Installment.status == InstallmentStatus.PENDING,
                    )
                )
                .options(selectinload(Installment.expense))
            )
            return list(result.scalars().all())

    @staticmethod
    def _add_months(source_date: datetime, months: int) -> datetime:
        """Add calendar months to a date, clamping day to month max."""
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        days_in_month = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        day = min(source_date.day, days_in_month[month - 1])
        return source_date.replace(year=year, month=month, day=day)
