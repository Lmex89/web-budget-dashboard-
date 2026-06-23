"""Expense API endpoints.

Thin route handlers — delegates all business logic to ExpenseService,
InstallmentService, and AnalyticsService.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from app.dependencies.auth import get_current_active_user
from app.dependencies.services import (
    get_expense_service,
    get_installment_service,
    get_analytics_service,
)
from app.domains.services.expense_service import ExpenseService
from app.domains.services.installment_service import InstallmentService
from app.domains.services.analytics_service import AnalyticsService
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
)
from app.schemas.common import BaseResponse, PaginatedResponse
from app.models import User

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse)
async def list_expenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="ISO format date"),
    end_date: Optional[str] = Query(None, description="ISO format date"),
    credit_card_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    service: ExpenseService = Depends(get_expense_service),
):
    logger.info(f"GET /expenses - user={current_user.id}, page={page}, size={page_size}")
    expenses, total = await service.list_by_family(
        family_id=current_user.family_id,
        page=page,
        page_size=page_size,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        credit_card_id=credit_card_id,
    )

    return PaginatedResponse(
        data=[
            {
                "id": e.id,
                "amount": e.amount,
                "description": e.description,
                "date": e.date,
                "payment_method": e.payment_method,
                "category_id": e.category_id,
                "category_name": e.category.name,
                "user_name": e.user.full_name,
                "credit_card_id": e.credit_card_id,
                "created_at": e.created_at,
            }
            for e in expenses
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.post("", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    service: ExpenseService = Depends(get_expense_service),
):
    logger.info(f"POST /expenses - user={current_user.id}, amount={data.amount}")
    expense = await service.create(
        data=data,
        family_id=current_user.family_id,
        user_id=current_user.id,
    )
    return BaseResponse(data=ExpenseResponse.model_validate(expense))


@router.get("/{expense_id}", response_model=BaseResponse)
async def get_expense(
    expense_id: str,
    current_user: User = Depends(get_current_active_user),
    service: ExpenseService = Depends(get_expense_service),
):
    logger.info(f"GET /expenses/{expense_id} - user={current_user.id}")
    expense = await service.get_by_id(expense_id, current_user.family_id)
    return BaseResponse(data=ExpenseResponse.model_validate(expense))


@router.put("/{expense_id}", response_model=BaseResponse)
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    service: ExpenseService = Depends(get_expense_service),
):
    logger.info(f"PUT /expenses/{expense_id} - user={current_user.id}")
    expense = await service.update(
        expense_id, data, current_user.family_id, current_user.id
    )
    return BaseResponse(data=ExpenseResponse.model_validate(expense))


@router.delete("/{expense_id}", response_model=BaseResponse)
async def delete_expense(
    expense_id: str,
    current_user: User = Depends(get_current_active_user),
    service: ExpenseService = Depends(get_expense_service),
):
    logger.warning(f"DELETE /expenses/{expense_id} - user={current_user.id}")
    await service.delete(expense_id, current_user.family_id, current_user.id)
    return BaseResponse(data={"deleted": True})


# ── Export ────────────────────────────────────────────────────────────────────

@router.get("/export/csv")
async def export_expenses_csv(
    category_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="ISO format date"),
    end_date: Optional[str] = Query(None, description="ISO format date"),
    current_user: User = Depends(get_current_active_user),
    service: ExpenseService = Depends(get_expense_service),
):
    logger.info(f"GET /expenses/export/csv - user={current_user.id}")
    expenses = await service.list_by_family_csv(
        family_id=current_user.family_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
    )

    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Description", "Category", "Amount", "Payment Method", "Paid By"])
    for e in expenses:
        writer.writerow([
            e.date.isoformat() if hasattr(e.date, "isoformat") else str(e.date),
            e.description or "",
            e.category.name if e.category else "",
            str(e.amount),
            e.payment_method.value if hasattr(e.payment_method, "value") else e.payment_method,
            e.user.full_name if e.user else "",
        ])

    output.seek(0)
    from fastapi.responses import Response
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )


# ── Analytics ─────────────────────────────────────────────────────────────────

@router.get("/analytics/monthly-summary", response_model=BaseResponse)
async def monthly_summary(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    category_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    logger.info(f"GET /expenses/analytics/monthly-summary - period={year}-{month:02d}")
    summary = await service.monthly_summary(current_user.family_id, year, month, category_id)
    return BaseResponse(data=summary)


@router.get("/analytics/category-distribution", response_model=BaseResponse)
async def category_distribution(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    category_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    logger.info(
        f"GET /expenses/analytics/category-distribution - period={year}-{month:02d}"
    )
    distribution = await service.category_distribution(
        current_user.family_id, year, month, category_id
    )
    return BaseResponse(data=distribution)


@router.get("/analytics/monthly-trend", response_model=BaseResponse)
async def monthly_trend(
    year: int = Query(..., ge=2020, le=2100),
    current_user: User = Depends(get_current_active_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    logger.info(f"GET /expenses/analytics/monthly-trend - year={year}")
    trend = await service.monthly_trend(current_user.family_id, year)
    return BaseResponse(data=trend)


# ── Installments ──────────────────────────────────────────────────────────────

@router.get("/installments/overdue", response_model=BaseResponse)
async def overdue_installments(
    current_user: User = Depends(get_current_active_user),
    service: InstallmentService = Depends(get_installment_service),
):
    logger.info(f"GET /expenses/installments/overdue - user={current_user.id}")
    overdue = await service.get_overdue(current_user.family_id)
    return BaseResponse(
        data=[
            {
                "id": i.id,
                "amount": str(i.amount),
                "due_date": i.due_date.isoformat(),
                "installment_number": i.installment_number,
                "total_installments": i.total_installments,
                "expense_id": i.expense_id,
            }
            for i in overdue
        ]
    )
