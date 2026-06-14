from fastapi import APIRouter, Depends, status
from loguru import logger

from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_debt_service
from app.domains.services.debt_service import DebtService
from app.models import User
from app.schemas.common import BaseResponse
from app.schemas.debt import DebtCreate, DebtResponse

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get("", response_model=BaseResponse)
async def list_debts(
    current_user: User = Depends(get_current_active_user),
    service: DebtService = Depends(get_debt_service),
):
    logger.info(f"GET /debts - family={current_user.family_id}")
    debts = await service.list_by_family(current_user.family_id)
    return BaseResponse(data=[DebtResponse.model_validate(d).model_dump() for d in debts])


@router.post("", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_debt(
    data: DebtCreate,
    current_user: User = Depends(get_current_active_user),
    service: DebtService = Depends(get_debt_service),
):
    logger.info(f"POST /debts - family={current_user.family_id}, name={data.name}")
    debt = await service.create(
        data=data,
        family_id=current_user.family_id,
        created_by_user_id=current_user.id,
    )
    return BaseResponse(data=DebtResponse.model_validate(debt).model_dump())
