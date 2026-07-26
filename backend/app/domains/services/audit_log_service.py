"""Audit log service.

SRP: Single responsibility for family-scoped audit log queries.
OCP: Open for extension via dependency injection of IUnitOfWork.
DIP: Depends on IUnitOfWork abstraction, not concrete repositories.
"""
from typing import List, Optional

from loguru import logger

from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import AuditLog


class AuditLogService:
    """Manages read-only access to audit log entries for a family."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def list_by_family(
        self,
        family_id: str,
        page: int = 1,
        page_size: int = 25,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[List[AuditLog], int]:
        """Paginated list of audit logs for the given family."""
        logger.info(f"Listing audit logs: family={family_id}, page={page}, size={page_size}")
        async with self.uow:
            return await self.uow.audit_logs.get_by_family(
                family_id, page, page_size, entity_type, action,
            )
