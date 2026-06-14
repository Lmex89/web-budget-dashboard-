from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from loguru import logger
from app.db.session import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.models import User

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        logger.warning("Authentication attempt without token")
        raise UnauthorizedException("Authentication token missing.")

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            logger.warning(f"Token missing 'sub' claim: {payload}")
            raise UnauthorizedException("Invalid token payload.")
        logger.debug(f"Token decoded for user: {user_id}")
    except Exception:
        logger.exception("Token validation failed")
        raise UnauthorizedException("Invalid token.")
    
    try:
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.family))
        )
        user = result.scalar_one_or_none()
    except Exception:
        logger.exception("Database error fetching user {}", user_id)
        raise UnauthorizedException("Authentication service unavailable.")

    if not user:
        logger.warning(f"User from token not found: id={user_id}")
        raise UnauthorizedException("User not found.")

    if not user.is_active:
        logger.warning(f"Inactive user attempted access: id={user.id}, email={user.email}")
        raise UnauthorizedException("User is inactive.")

    logger.debug(f"Authenticated user: id={user.id}, email={user.email}, family={user.family_id}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin privileges required.")
    logger.debug(f"Admin access granted: user={current_user.id}")
    return current_user
