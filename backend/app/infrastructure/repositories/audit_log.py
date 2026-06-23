from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.audit_log import AuditLogRepository
from app.models import AuditLog
from app.core.exceptions import AppException


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

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
