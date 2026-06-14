"""Debt service for debt listing and creation."""

from decimal import Decimal

from loguru import logger

from app.core.exceptions import ValidationException
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import Debt, DebtStatus
from app.schemas.debt import DebtCreate


class DebtService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def list_by_family(self, family_id: str) -> list[Debt]:
        logger.info(f"Listing debts for family={family_id}")
        async with self.uow:
            return await self.uow.debts.get_by_family(family_id)

    async def create(self, data: DebtCreate, family_id: str, created_by_user_id: str) -> Debt:
        logger.info(f"Creating debt name={data.name}, family={family_id}, type={data.type}")

        remaining_amount = data.remaining_amount
        if remaining_amount is None:
            remaining_amount = data.original_amount

        if remaining_amount > data.original_amount:
            raise ValidationException("remaining_amount cannot be greater than original_amount")

        status = data.status or DebtStatus.ACTIVE
        if remaining_amount == Decimal("0"):
            status = DebtStatus.PAID

        async with self.uow:
            debt = Debt(
                name=data.name,
                description=data.description,
                original_amount=data.original_amount,
                remaining_amount=remaining_amount,
                currency=data.currency,
                type=data.type,
                status=status,
                counterparty_name=data.counterparty_name,
                family_id=family_id,
                created_by_user_id=created_by_user_id,
            )
            return await self.uow.debts.create(debt)
