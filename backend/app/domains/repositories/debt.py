from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Debt


class DebtRepository(ABC):
    @abstractmethod
    async def get_by_id(self, debt_id: str) -> Optional[Debt]:
        pass

    @abstractmethod
    async def get_by_family(self, family_id: str) -> List[Debt]:
        pass

    @abstractmethod
    async def create(self, debt: Debt) -> Debt:
        pass

    @abstractmethod
    async def update(self, debt: Debt) -> Debt:
        pass

    @abstractmethod
    async def delete(self, debt_id: str) -> bool:
        pass

    @abstractmethod
    async def update_remaining_amount(self, debt_id: str, new_amount: float) -> Debt:
        pass
