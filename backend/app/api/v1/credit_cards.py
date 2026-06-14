from fastapi import APIRouter, Depends, status
from loguru import logger

from app.dependencies.auth import get_current_active_user
from app.dependencies.services import get_credit_card_service
from app.domains.services.credit_card_service import CreditCardService
from app.models import User
from app.schemas.common import BaseResponse
from app.schemas.credit_card import CreditCardCreate, CreditCardResponse

router = APIRouter(prefix="/credit-cards", tags=["Credit Cards"])


@router.get("", response_model=BaseResponse)
async def list_credit_cards(
    current_user: User = Depends(get_current_active_user),
    service: CreditCardService = Depends(get_credit_card_service),
):
    logger.info(f"GET /credit-cards - family={current_user.family_id}")
    cards = await service.list_by_family(current_user.family_id)
    return BaseResponse(data=[CreditCardResponse.model_validate(c).model_dump() for c in cards])


@router.post("", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_credit_card(
    data: CreditCardCreate,
    current_user: User = Depends(get_current_active_user),
    service: CreditCardService = Depends(get_credit_card_service),
):
    logger.info(f"POST /credit-cards - family={current_user.family_id}, name={data.name}")
    card = await service.create(data, current_user.family_id)
    return BaseResponse(data=CreditCardResponse.model_validate(card).model_dump())
