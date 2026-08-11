from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from loguru import logger
from app.db.session import get_db
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token
from app.models import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    if not token:
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
            .where(User.id == user_id, User.deleted_at.is_(None))
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
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin privileges required.")
    logger.debug(f"Admin access granted: user={current_user.id}")
    return current_user


def require_roles(*allowed_roles: UserRole):
    async def role_dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            roles = ", ".join(role.value for role in allowed_roles)
            raise ForbiddenException(f"Requires one of roles: {roles}.")
        return current_user

    return role_dependency
