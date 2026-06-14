from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from loguru import logger
from app.domains.repositories.user import UserRepository
from app.models import User
from app.core.exceptions import NotFoundException, AppException


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        logger.debug(f"Querying user by id: {user_id}")
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            logger.exception(f"Database error fetching user {user_id}")
            raise AppException("ERR_DATABASE", "Failed to fetch user.")

    async def get_by_email(self, email: str) -> Optional[User]:
        logger.debug(f"Querying user by email: {email}")
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            logger.exception("Database error fetching user by email")
            raise AppException("ERR_DATABASE", "Failed to fetch user by email.")

    async def create(self, user: User) -> User:
        logger.info(f"Creating user: email={user.email}, name={user.full_name}, family={user.family_id}")
        try:
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)
            logger.info(f"User created: id={user.id}, email={user.email}")
            return user
        except SQLAlchemyError:
            logger.exception("Database error creating user")
            raise AppException("ERR_DATABASE", "Failed to create user.")

    async def update(self, user: User) -> User:
        logger.info(f"Updating user: id={user.id}")
        try:
            await self.db.flush()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            logger.exception(f"Database error updating user {user.id}")
            raise AppException("ERR_DATABASE", "Failed to update user.")

    async def delete(self, user_id: str) -> bool:
        logger.warning(f"Deleting user: id={user_id}")
        try:
            user = await self.get_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            await self.db.delete(user)
            await self.db.flush()
            return True
        except NotFoundException:
            raise
        except SQLAlchemyError:
            logger.exception(f"Database error deleting user {user_id}")
            raise AppException("ERR_DATABASE", "Failed to delete user.")

    async def get_by_family(self, family_id: str) -> List[User]:
        logger.debug(f"Querying users for family: {family_id}")
        try:
            result = await self.db.execute(
                select(User)
                .where(User.family_id == family_id)
                .options(selectinload(User.family))
                .order_by(User.full_name)
            )
            users = list(result.scalars().all())
            logger.debug(f"Found {len(users)} users in family {family_id}")
            return users
        except SQLAlchemyError:
            logger.exception("Database error listing family users")
            raise AppException("ERR_DATABASE", "Failed to list family users.")
