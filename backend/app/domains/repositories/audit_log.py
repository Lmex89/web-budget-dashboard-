from abc import ABC, abstractmethod

from app.models import AuditLog


class AuditLogRepository(ABC):
    @abstractmethod
    async def create(self, audit_log: AuditLog) -> AuditLog:
        pass
