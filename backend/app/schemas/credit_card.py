from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreditCardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    last_four_digits: str | None = Field(default=None, pattern=r"^\d{4}$")
    limit: Decimal = Field(..., gt=0, decimal_places=2, max_digits=15)
    closing_day: int = Field(..., ge=1, le=31)
    due_day: int = Field(..., ge=1, le=31)
    current_balance: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2, max_digits=15)


class CreditCardResponse(BaseModel):
    id: str
    name: str
    last_four_digits: str | None
    limit: Decimal
    closing_day: int
    due_day: int
    current_balance: Decimal
    family_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
