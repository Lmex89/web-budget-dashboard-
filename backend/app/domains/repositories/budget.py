from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Budget, BudgetCategory


class BudgetRepository(ABC):
    @abstractmethod
    async def get_by_id(self, budget_id: str) -> Optional[Budget]:
        pass

    @abstractmethod
    async def get_by_period(
        self,
        family_id: str,
        year: int,
        month: int,
        include_deleted: bool = False,
    ) -> Optional[Budget]:
        pass

    @abstractmethod
    async def list_by_family(self, family_id: str, year: Optional[int] = None) -> List[Budget]:
        pass

    @abstractmethod
    async def create(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    async def update(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    async def delete(self, budget_id: str) -> bool:
        pass

    @abstractmethod
    async def add_category(self, entry: BudgetCategory) -> BudgetCategory:
        pass

    @abstractmethod
    async def get_category_entry(
        self,
        budget_id: str,
        category_id: str,
        include_deleted: bool = False,
    ) -> Optional[BudgetCategory]:
        pass

    @abstractmethod
    async def delete_category(self, entry: BudgetCategory) -> bool:
        pass
