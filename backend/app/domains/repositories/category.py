from abc import ABC, abstractmethod
from typing import Optional

from app.models import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        pass

    @abstractmethod
    async def get_by_family(self, family_id: str) -> list[Category]:
        pass

    @abstractmethod
    async def exists_by_name(self, family_id: str, name: str) -> bool:
        pass

    @abstractmethod
    async def create(self, category: Category) -> Category:
        pass
