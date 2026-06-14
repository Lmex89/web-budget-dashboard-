from abc import ABC, abstractmethod
from typing import Optional

from app.models import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        pass
