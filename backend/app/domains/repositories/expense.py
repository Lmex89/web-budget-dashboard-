from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Expense


class ExpenseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, expense_id: str) -> Optional[Expense]:
        pass

    @abstractmethod
    async def get_by_family(
        self,
        family_id: str,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        credit_card_id: Optional[str] = None,
    ) -> tuple[List[Expense], int]:
        pass

    @abstractmethod
    async def get_by_family_csv(
        self,
        family_id: str,
        category_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Expense]:
        pass

    @abstractmethod
    async def create(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def update(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def delete(self, expense_id: str) -> bool:
        pass

    @abstractmethod
    async def get_family_monthly_summary(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> dict:
        pass

    @abstractmethod
    async def get_category_distribution(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> List[dict]:
        pass
