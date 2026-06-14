"""Authentication and user management API endpoints."""
import uuid

from fastapi import APIRouter, Depends, Response, status
from loguru import logger

from app.dependencies.auth import get_current_active_user, require_admin
from app.dependencies.unit_of_work import get_unit_of_work
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserAddToFamily
from app.schemas.common import BaseResponse
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.exceptions import (
    InvalidCredentialsException,
    EmailAlreadyRegisteredException,
    UnauthorizedException,
)
from app.core.config import settings
from app.models import User, Family

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Register a new user and create a new family."""
    logger.info(f"Registering user: email={data.email}")
    async with uow:
        existing = await uow.users.get_by_email(data.email)
        if existing:
            raise EmailAlreadyRegisteredException(data.email)

        family = Family(id=str(uuid.uuid4()), name=data.family_name)
        uow._session.add(family)
        await uow._session.flush()

        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            family_id=family.id,
            is_admin=True,
        )
        uow._session.add(user)

    logger.info(f"User registered: id={user.id}, email={user.email}, family={family.id}")
    return BaseResponse(data=UserResponse.model_validate(user).model_dump())


@router.post("/login", response_model=BaseResponse)
async def login(
    data: UserLogin,
    response: Response,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Authenticate user and set JWT cookie."""
    logger.info(f"Login attempt: email={data.email}")
    async with uow:
        user = await uow.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()
        if not user.is_active:
            raise UnauthorizedException("Account is inactive.")

    token = create_access_token({"sub": user.id, "family_id": user.family_id})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    logger.info(f"Login successful: id={user.id}, email={user.email}")
    return BaseResponse(data=UserResponse.model_validate(user).model_dump())


@router.get("/me", response_model=BaseResponse)
async def me(current_user: User = Depends(get_current_active_user)):
    """Return the authenticated user's profile."""
    return BaseResponse(data=UserResponse.model_validate(current_user).model_dump())


@router.post("/logout", response_model=BaseResponse)
async def logout(response: Response):
    """Clear the JWT cookie."""
    response.delete_cookie("access_token")
    return BaseResponse(data={"message": "Logged out"})


# ── Family user management (admin only) ─────────────────────────────────────

@router.get("/users", response_model=BaseResponse)
async def list_family_users(
    current_user: User = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """List all users in the current user's family."""
    logger.info(f"Listing family users: family={current_user.family_id}")
    async with uow:
        users = await uow.users.get_by_family(current_user.family_id)
        return BaseResponse(
            data=[UserResponse.model_validate(u).model_dump() for u in users]
        )


@router.post("/users", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_family(
    data: UserAddToFamily,
    current_user: User = Depends(get_current_active_user),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Add a new user to the existing family (admin only)."""
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Only family admins can add users.")

    logger.info(f"Adding user to family: email={data.email}, family={current_user.family_id}")
    async with uow:
        existing = await uow.users.get_by_email(data.email)
        if existing:
            raise EmailAlreadyRegisteredException(data.email)

        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            family_id=current_user.family_id,
            is_admin=False,
        )
        uow._session.add(user)

    logger.info(f"User added to family: id={user.id}, email={user.email}")
    return BaseResponse(data=UserResponse.model_validate(user).model_dump())
