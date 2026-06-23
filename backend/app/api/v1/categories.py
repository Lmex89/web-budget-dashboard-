from fastapi import APIRouter, Depends, status
from loguru import logger

from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_category_service
from app.domains.services.category_service import CategoryService
from app.models import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import BaseResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=BaseResponse)
async def list_categories(
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service),
):
    logger.info(f"GET /categories - family={current_user.family_id}")
    categories = await service.list_by_family(current_user.family_id)
    return BaseResponse(data=[CategoryResponse.model_validate(c).model_dump() for c in categories])


@router.post("", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service),
):
    logger.info(f"POST /categories - family={current_user.family_id}, name={data.name}")
    category = await service.create(data, current_user.family_id)
    return BaseResponse(data=CategoryResponse.model_validate(category).model_dump())


@router.put("/{category_id}", response_model=BaseResponse)
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service),
):
    logger.info(f"PUT /categories/{category_id} - family={current_user.family_id}, name={data.name}")
    category = await service.update(category_id, data, current_user.family_id)
    return BaseResponse(data=CategoryResponse.model_validate(category).model_dump())
