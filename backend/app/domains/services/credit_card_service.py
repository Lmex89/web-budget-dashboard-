"""Credit card service for listing and creation."""

from loguru import logger

from app.core.exceptions import ConflictException
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import CreditCard
from app.schemas.credit_card import CreditCardCreate


class CreditCardService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def list_by_family(self, family_id: str) -> list[CreditCard]:
        logger.info(f"Listing credit cards for family={family_id}")
        async with self.uow:
            return await self.uow.credit_cards.get_by_family(family_id)

    async def create(self, data: CreditCardCreate, family_id: str) -> CreditCard:
        logger.info(f"Creating credit card name={data.name}, family={family_id}")
        async with self.uow:
            exists = await self.uow.credit_cards.exists_by_name(family_id, data.name)
            if exists:
                raise ConflictException(f"Credit card '{data.name}' already exists.")

            card = CreditCard(
                name=data.name,
                last_four_digits=data.last_four_digits,
                limit=data.limit,
                closing_day=data.closing_day,
                due_day=data.due_day,
                current_balance=data.current_balance,
                family_id=family_id,
            )
            return await self.uow.credit_cards.create(card)
