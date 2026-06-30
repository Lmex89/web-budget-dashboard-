from abc import ABC, abstractmethod
from typing import List

from app.models import Installment


class InstallmentRepository(ABC):
    @abstractmethod
    async def get_by_expense(self, expense_id: str) -> List[Installment]:
        pass

    @abstractmethod
    async def get_overdue_by_family(self, family_id: str) -> List[Installment]:
        pass

    @abstractmethod
    async def create(self, installment: Installment) -> Installment:
        pass

    @abstractmethod
    async def create_many(self, installments: List[Installment]) -> None:
        pass
