from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    family_name: str = Field(..., min_length=1, max_length=255)


class UserAddToFamily(UserBase):
    """Add a user to an existing family (admin action)."""
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    family_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
