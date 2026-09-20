from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field


class BudgetCategoryItem(BaseModel):
    category_id: str
    amount: Decimal = Field(..., ge=0, decimal_places=2, max_digits=15)


class BudgetUpsert(BaseModel):
    total_budget: Decimal = Field(..., gt=0, decimal_places=2, max_digits=15)
    categories: List[BudgetCategoryItem] = []
