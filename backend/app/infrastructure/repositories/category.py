from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.category import CategoryRepository
from app.models import Category
from app.core.exceptions import AppException

class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        logger.debug(f"Querying category by id: {category_id}")
        try:
            result = await self.db.execute(
                select(Category).where(Category.id == category_id)
            )
            category = result.scalar_one_or_none()
            logger.debug(f"Category {category_id}: {'found' if category else 'not found'}")
            return category
        except SQLAlchemyError:
            logger.exception(f"Database error fetching category {category_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch category.")
