from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.family import FamilyRepository
from app.models import Family
from app.core.exceptions import AppException


class SQLAlchemyFamilyRepository(FamilyRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _active_filter(self):
        return Family.deleted_at.is_(None)

    async def create(self, family: Family) -> Family:
        logger.info(f"Creating family: name={family.name}")
        try:
            self.db.add(family)
            await self.db.flush()
            await self.db.refresh(family)
            logger.info(f"Family created: id={family.id}, name={family.name}")
            return family
        except SQLAlchemyError:
            logger.exception("Database error creating family")
            raise AppException("ERR_DATABASE", "Failed to create family.")
