from typing import Optional

from sqlalchemy import select, func
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

    async def get_by_family(self, family_id: str) -> list[Category]:
        logger.debug(f"Querying categories for family: {family_id}")
        try:
            result = await self.db.execute(
                select(Category)
                .where(Category.family_id == family_id)
                .order_by(Category.name.asc())
            )
            categories = list(result.scalars().all())
            logger.debug(f"Found {len(categories)} categories for family {family_id}")
            return categories
        except SQLAlchemyError:
            logger.exception("Database error listing categories")
            raise AppException("ERR_DATABASE", "Failed to list categories.")

    async def exists_by_name(self, family_id: str, name: str) -> bool:
        logger.debug(f"Checking category name existence: family={family_id}, name={name}")
        try:
            result = await self.db.execute(
                select(func.count(Category.id)).where(
                    Category.family_id == family_id,
                    Category.name == name,
                    Category.parent_id.is_(None),
                )
            )
            count = result.scalar_one()
            return count > 0
        except SQLAlchemyError:
            logger.exception("Database error checking category name")
            raise AppException("ERR_DATABASE", "Failed to validate category name.")

    async def create(self, category: Category) -> Category:
        logger.info(f"Creating category: name={category.name}, family={category.family_id}")
        try:
            self.db.add(category)
            await self.db.flush()
            await self.db.refresh(category)
            return category
        except SQLAlchemyError:
            logger.exception("Database error creating category")
            raise AppException("ERR_DATABASE", "Failed to create category.")
