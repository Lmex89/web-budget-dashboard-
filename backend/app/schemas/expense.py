from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PaymentMethod


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=15)
    description: Optional[str] = Field(None, max_length=1000)
    date: datetime
    payment_method: PaymentMethod
    category_id: str
    credit_card_id: Optional[str] = None
    is_installment: bool = False
    total_installments: Optional[int] = Field(None, ge=2, le=48)
    
    @field_validator('total_installments')
    @classmethod
    def validate_installments(cls, v, info):
        is_installment = info.data.get('is_installment')
        if is_installment and (v is None or v < 2):
            raise ValueError('total_installments must be >= 2 when is_installment is true')
        if not is_installment and v is not None:
            return None
        return v
    
    @field_validator('credit_card_id')
    @classmethod
    def validate_credit_card_for_installment(cls, v, info):
        payment_method = info.data.get('payment_method')
        is_installment = info.data.get('is_installment')
        if is_installment and payment_method != PaymentMethod.CREDIT:
            raise ValueError('Installments are only allowed with credit card payment')
        if payment_method == PaymentMethod.CREDIT and not v:
            raise ValueError('credit_card_id is required for credit card payments')
        return v


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, max_digits=15)
    description: Optional[str] = Field(None, max_length=1000)
    date: Optional[datetime] = None
    payment_method: Optional[PaymentMethod] = None
    category_id: Optional[str] = None
    credit_card_id: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: str
    amount: Decimal
    description: Optional[str]
    date: datetime
    payment_method: PaymentMethod
    is_installment: bool
    total_installments: Optional[int]
    installment_number: Optional[int]
    user_id: str
    category_id: str
    credit_card_id: Optional[str]
    family_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


