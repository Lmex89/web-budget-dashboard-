from abc import ABC, abstractmethod
from typing import Optional

from app.models import CreditCard


class CreditCardRepository(ABC):
    @abstractmethod
    async def get_by_id(self, card_id: str) -> Optional[CreditCard]:
        pass

    @abstractmethod
    async def get_by_family(self, family_id: str) -> list[CreditCard]:
        pass

    @abstractmethod
    async def exists_by_name(self, family_id: str, name: str) -> bool:
        pass

    @abstractmethod
    async def create(self, card: CreditCard) -> CreditCard:
        pass
