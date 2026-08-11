"""Authentication and user management API endpoints."""
import uuid

from fastapi import APIRouter, Depends, Response, status
from loguru import logger

from app.dependencies.auth import get_current_active_user, require_admin
from app.dependencies.unit_of_work import get_unit_of_work
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserAddToFamily,
    UserUpdateRole,
    TokenResponse,
)
from app.schemas.common import BaseResponse
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.exceptions import (
    InvalidCredentialsException,
    EmailAlreadyRegisteredException,
    UnauthorizedException,
    ForbiddenException,
)
from app.core.config import settings
from app.models import User, Family, UserRole

auth_public_router = APIRouter(prefix="/auth", tags=["Auth"])
auth_protected_router = APIRouter(
    prefix="/auth", tags=["Auth"],
    dependencies=[Depends(get_current_active_user)],
)


@auth_public_router.post("/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
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
        await uow.families.create(family)

        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            family_id=family.id,
            role=UserRole.ADMIN,
        )
        await uow.users.create(user)

    logger.info(f"User registered: id={user.id}, email={user.email}, family={family.id}")
    return BaseResponse(data=UserResponse.model_validate(user).model_dump())


@auth_public_router.post("/login", response_model=BaseResponse)
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

    token = create_access_token({"sub": user.id, "family_id": user.family_id, "role": user.role.value})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    logger.info(f"Login successful: id={user.id}, email={user.email}")
    user_resp = UserResponse.model_validate(user)
    token_data = TokenResponse(access_token=token, token_type="bearer", user=user_resp)
    return BaseResponse(data=token_data.model_dump())


@auth_protected_router.get("/me", response_model=BaseResponse)
async def me(current_user: User = Depends(get_current_active_user)):
    """Return the authenticated user's profile."""
    return BaseResponse(data=UserResponse.model_validate(current_user).model_dump())


@auth_public_router.post("/logout", response_model=BaseResponse)
async def logout(response: Response):
    """Clear the JWT cookie."""
    response.delete_cookie("access_token")
    return BaseResponse(data={"message": "Logged out"})


# ── Family user management (admin only) ─────────────────────────────────────

@auth_protected_router.get("/users", response_model=BaseResponse)
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


@auth_protected_router.post("/users", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_family(
    data: UserAddToFamily,
    current_user: User = Depends(require_admin),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Add a new user to the existing family (admin only)."""
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
            role=data.role,
        )
        await uow.users.create(user)

    logger.info(f"User added to family: id={user.id}, email={user.email}")
    return BaseResponse(data=UserResponse.model_validate(user).model_dump())


@auth_protected_router.patch("/users/{user_id}/role", response_model=BaseResponse)
async def update_user_role(
    user_id: str,
    data: UserUpdateRole,
    current_user: User = Depends(require_admin),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Update a family user's role (admin only)."""
    logger.info(f"Updating user role: user={user_id}, role={data.role.value}, actor={current_user.id}")
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user or user.family_id != current_user.family_id:
            raise ForbiddenException("Cannot update role for users outside your family.")
        user.role = data.role
        await uow.users.update(user)

    return BaseResponse(data=UserResponse.model_validate(user).model_dump())


@auth_protected_router.patch("/users/{user_id}/deactivate", response_model=BaseResponse)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Deactivate a family user (admin only)."""
    if user_id == current_user.id:
        raise ForbiddenException("You cannot deactivate your own account.")

    logger.info(f"Deactivating user: user={user_id}, actor={current_user.id}")
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user or user.family_id != current_user.family_id:
            raise ForbiddenException("Cannot deactivate users outside your family.")
        user.is_active = False
        await uow.users.update(user)

    return BaseResponse(data=UserResponse.model_validate(user).model_dump())


@auth_protected_router.patch("/users/{user_id}/activate", response_model=BaseResponse)
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """Activate a family user (admin only)."""
    logger.info(f"Activating user: user={user_id}, actor={current_user.id}")
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user or user.family_id != current_user.family_id:
            raise ForbiddenException("Cannot activate users outside your family.")
        user.is_active = True
        await uow.users.update(user)

    return BaseResponse(data=UserResponse.model_validate(user).model_dump())
