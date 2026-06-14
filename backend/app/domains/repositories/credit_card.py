from abc import ABC, abstractmethod
from typing import Optional

from app.models import CreditCard


class CreditCardRepository(ABC):
    @abstractmethod
    async def get_by_id(self, card_id: str) -> Optional[CreditCard]:
        pass
