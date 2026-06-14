from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.credit_card import CreditCardRepository
from app.models import CreditCard
from app.core.exceptions import AppException

class SQLAlchemyCreditCardRepository(CreditCardRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, card_id: str) -> Optional[CreditCard]:
        logger.debug(f"Querying credit card by id: {card_id}")
        try:
            result = await self.db.execute(
                select(CreditCard).where(CreditCard.id == card_id)
            )
            card = result.scalar_one_or_none()
            return card
        except SQLAlchemyError:
            logger.exception(f"Database error fetching credit card {card_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch credit card.")
