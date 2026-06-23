from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(default=None, max_length=50)


class CategoryUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    id: str
    name: str
    color: Optional[str]
    icon: Optional[str]
    family_id: str
    parent_id: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
