from typing import List, Optional

from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.audit_log import AuditLogRepository
from app.models import AuditLog, User
from app.core.exceptions import AppException


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _active_filter(self):
        return AuditLog.deleted_at.is_(None)

    async def create(self, audit_log: AuditLog) -> AuditLog:
        logger.debug(f"Persisting audit log: entity={audit_log.entity_type}/{audit_log.entity_id}, action={audit_log.action}")
        try:
            self.db.add(audit_log)
            await self.db.flush()
            await self.db.refresh(audit_log)
            logger.debug(f"Audit log persisted: id={audit_log.id}")
            return audit_log
        except SQLAlchemyError:
            logger.exception("Database error creating audit log")
            raise AppException("ERR_DATABASE", "Failed to create audit log.")

    async def get_by_family(
        self,
        family_id: str,
        page: int = 1,
        page_size: int = 25,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[List[AuditLog], int]:
        conditions = [User.family_id == family_id, self._active_filter()]

        if entity_type:
            conditions.append(AuditLog.entity_type == entity_type)
            logger.debug(f"Filtering audit logs by entity_type: {entity_type}")
        if action:
            conditions.append(AuditLog.action == action)
            logger.debug(f"Filtering audit logs by action: {action}")

        try:
            count_stmt = (
                select(func.count())
                .select_from(AuditLog)
                .join(User, AuditLog.user_id == User.id)
                .where(and_(*conditions))
            )
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar()
            logger.debug(f"Total audit logs matching filter: {total}")

            stmt = (
                select(AuditLog)
                .join(User, AuditLog.user_id == User.id)
                .where(and_(*conditions))
                .options(joinedload(AuditLog.user))
                .order_by(desc(AuditLog.created_at))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )

            result = await self.db.execute(stmt)
            audit_logs = result.scalars().unique().all()
            logger.debug(f"Returning {len(audit_logs)} audit logs (page {page}/{(total + page_size - 1) // page_size})")
            return list(audit_logs), total
        except SQLAlchemyError:
            logger.exception("Database error listing audit logs")
            raise AppException("ERR_DATABASE", "Failed to list audit logs.")
