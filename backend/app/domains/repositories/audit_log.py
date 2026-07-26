from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import AuditLog


class AuditLogRepository(ABC):
    @abstractmethod
    async def create(self, audit_log: AuditLog) -> AuditLog:
        pass

    @abstractmethod
    async def get_by_family(
        self,
        family_id: str,
        page: int = 1,
        page_size: int = 25,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[List[AuditLog], int]:
        pass
