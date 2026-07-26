"""Category service for category listing and creation."""

from loguru import logger

from app.core.exceptions import CategoryInUseException, CategoryNotFoundException, ConflictException, ForbiddenException
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


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

    async def update(self, category_id: str, data: CategoryUpdate, family_id: str) -> Category:
        logger.info(f"Updating category id={category_id}, family={family_id}")
        async with self.uow:
            category = await self.uow.categories.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundException(category_id)
            if category.family_id != family_id:
                raise ForbiddenException("This category does not belong to your family.")

            if data.name is not None and category.name != data.name:
                exists = await self.uow.categories.exists_by_name(family_id, data.name)
                if exists:
                    raise ConflictException(f"Category '{data.name}' already exists.")

            if data.name is not None:
                category.name = data.name
            if data.color is not None:
                category.color = data.color
            if data.icon is not None:
                category.icon = data.icon
            return await self.uow.categories.update(category)

    async def delete(self, category_id: str, family_id: str) -> bool:
        logger.info(f"Deleting category id={category_id}, family={family_id}")
        async with self.uow:
            category = await self.uow.categories.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundException(category_id)
            if category.family_id != family_id:
                raise ForbiddenException("This category does not belong to your family.")

            if await self.uow.categories.has_expenses(category_id):
                raise CategoryInUseException(category.name)

            return await self.uow.categories.delete(category_id)
