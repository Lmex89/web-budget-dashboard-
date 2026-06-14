"""Dependency injection for domain services.

Assembles services with their UoW dependency via FastAPI Depends.
Each service is a callable that receives the IUnitOfWork.
"""
from fastapi import Depends

from app.dependencies.unit_of_work import get_unit_of_work
from app.domains.repositories.unit_of_work import IUnitOfWork
from app.domains.services.expense_service import ExpenseService
from app.domains.services.installment_service import InstallmentService
from app.domains.services.analytics_service import AnalyticsService
from app.domains.services.category_service import CategoryService
from app.domains.services.credit_card_service import CreditCardService


def get_expense_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> ExpenseService:
    return ExpenseService(uow)


def get_installment_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> InstallmentService:
    return InstallmentService(uow)


def get_analytics_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> AnalyticsService:
    return AnalyticsService(uow)


def get_category_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> CategoryService:
    return CategoryService(uow)


def get_credit_card_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> CreditCardService:
    return CreditCardService(uow)
