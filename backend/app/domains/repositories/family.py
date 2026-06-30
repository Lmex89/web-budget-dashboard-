from abc import ABC, abstractmethod

from app.models import Family


class FamilyRepository(ABC):
    @abstractmethod
    async def create(self, family: Family) -> Family:
        pass
