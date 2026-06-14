from typing import Any
from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    success: bool = True
    data: Any | None = None
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseResponse):
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
