from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.credit_card import CreditCardRepository
from app.models import CreditCard
from app.core.exceptions import AppException


class SQLAlchemyCreditCardRepository(CreditCardRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _active_filter(self):
        return CreditCard.deleted_at.is_(None)

    async def get_by_id(self, card_id: str) -> Optional[CreditCard]:
        logger.debug(f"Querying credit card by id: {card_id}")
        try:
            result = await self.db.execute(
                select(CreditCard).where(CreditCard.id == card_id, self._active_filter())
            )
            card = result.scalar_one_or_none()
            return card
        except SQLAlchemyError:
            logger.exception(f"Database error fetching credit card {card_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch credit card.")

    async def get_by_family(self, family_id: str) -> list[CreditCard]:
        logger.debug(f"Querying credit cards for family: {family_id}")
        try:
            result = await self.db.execute(
                select(CreditCard)
                .where(CreditCard.family_id == family_id, self._active_filter())
                .order_by(CreditCard.name.asc())
            )
            cards = list(result.scalars().all())
            logger.debug(f"Found {len(cards)} credit cards for family {family_id}")
            return cards
        except SQLAlchemyError:
            logger.exception("Database error listing credit cards")
            raise AppException("ERR_DATABASE", "Failed to list credit cards.")

    async def exists_by_name(self, family_id: str, name: str) -> bool:
        logger.debug(f"Checking credit card name existence: family={family_id}, name={name}")
        try:
            result = await self.db.execute(
                select(func.count(CreditCard.id)).where(
                    CreditCard.family_id == family_id,
                    func.lower(CreditCard.name) == name.lower(),
                    self._active_filter(),
                )
            )
            count = result.scalar_one()
            return count > 0
        except SQLAlchemyError:
            logger.exception("Database error checking credit card name")
            raise AppException("ERR_DATABASE", "Failed to validate credit card name.")

    async def create(self, card: CreditCard) -> CreditCard:
        logger.info(f"Creating credit card: name={card.name}, family={card.family_id}")
        try:
            self.db.add(card)
            await self.db.flush()
            await self.db.refresh(card)
            return card
        except SQLAlchemyError:
            logger.exception("Database error creating credit card")
            raise AppException("ERR_DATABASE", "Failed to create credit card.")
