"""Category service for category listing and creation."""

from loguru import logger

from app.core.exceptions import ConflictException
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import Category
from app.schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def list_by_family(self, family_id: str) -> list[Category]:
        logger.info(f"Listing categories for family={family_id}")
        async with self.uow:
            return await self.uow.categories.get_by_family(family_id)

    async def create(self, data: CategoryCreate, family_id: str) -> Category:
        logger.info(f"Creating category name={data.name}, family={family_id}")
        async with self.uow:
            exists = await self.uow.categories.exists_by_name(family_id, data.name)
            if exists:
                raise ConflictException(f"Category '{data.name}' already exists.")

            category = Category(
                name=data.name,
                color=data.color,
                icon=data.icon,
                family_id=family_id,
                parent_id=None,
            )
            return await self.uow.categories.create(category)
