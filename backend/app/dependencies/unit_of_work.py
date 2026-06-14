from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from app.db.session import get_db
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.infrastructure.repositories.unit_of_work import SQLAlchemyUnitOfWork

async def get_unit_of_work(db: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    logger.debug("Creating Unit of Work")
    return SQLAlchemyUnitOfWork(db)
