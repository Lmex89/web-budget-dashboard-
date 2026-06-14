from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import DebtStatus, DebtType


class DebtCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    original_amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=15)
    remaining_amount: Decimal | None = Field(default=None, ge=0, decimal_places=2, max_digits=15)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    type: DebtType
    status: DebtStatus | None = DebtStatus.ACTIVE
    counterparty_name: str | None = Field(default=None, max_length=255)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class DebtResponse(BaseModel):
    id: str
    name: str
    description: str | None
    original_amount: Decimal
    remaining_amount: Decimal
    currency: str
    type: DebtType
    status: DebtStatus
    counterparty_name: str | None
    family_id: str
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
