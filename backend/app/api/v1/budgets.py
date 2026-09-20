"""Budget API endpoints.

Thin route handlers — delegates all business logic to BudgetService.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from loguru import logger

from app.dependencies.auth import get_current_active_user, require_roles
from app.dependencies.services import get_budget_service
from app.domains.services.budget_service import BudgetService
from app.schemas.budget import BudgetUpsert
from app.schemas.common import BaseResponse
from app.core.serialization import to_jsonable
from app.models import Budget, User, UserRole

router = APIRouter(
    prefix="/budgets", tags=["Budgets"],
    dependencies=[Depends(get_current_active_user)],
)


def _serialize_budget(budget: Budget) -> dict:
    return {
        "id": budget.id,
        "family_id": budget.family_id,
        "year": budget.year,
        "month": budget.month,
        "total_budget": to_jsonable(budget.total_budget),
        "categories": [
            {
                "id": entry.id,
                "category_id": entry.category_id,
                "category_name": entry.category.name,
                "color": entry.category.color,
                "amount": to_jsonable(entry.amount),
            }
            for entry in budget.categories
        ],
        "created_at": budget.created_at,
        "updated_at": budget.updated_at,
    }


@router.get("", response_model=BaseResponse)
async def list_budgets(
    year: Optional[int] = Query(None, ge=2020, le=2100),
    current_user: User = Depends(get_current_active_user),
    service: BudgetService = Depends(get_budget_service),
):
    logger.info(f"GET /budgets - user={current_user.id}, year={year}")
    budgets = await service.list_by_family(current_user.family_id, year)
    return BaseResponse(data=[_serialize_budget(b) for b in budgets])


@router.get("/progress", response_model=BaseResponse)
async def budget_progress(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    service: BudgetService = Depends(get_budget_service),
):
    logger.info(f"GET /budgets/progress - user={current_user.id}, period={year}-{month:02d}")
    progress = await service.get_progress(current_user.family_id, year, month)
    return BaseResponse(data=to_jsonable(progress))


@router.put("/{year}/{month}", response_model=BaseResponse)
async def upsert_budget(
    data: BudgetUpsert,
    year: int = Path(..., ge=2020, le=2100),
    month: int = Path(..., ge=1, le=12),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    service: BudgetService = Depends(get_budget_service),
):
    logger.info(f"PUT /budgets/{year}/{month} - user={current_user.id}")
    budget = await service.upsert(current_user.family_id, current_user.id, year, month, data)
    return BaseResponse(data=_serialize_budget(budget))


@router.delete("/{budget_id}", response_model=BaseResponse)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    service: BudgetService = Depends(get_budget_service),
):
    logger.warning(f"DELETE /budgets/{budget_id} - user={current_user.id}")
    await service.delete(budget_id, current_user.family_id, current_user.id)
    return BaseResponse(data={"deleted": True})
