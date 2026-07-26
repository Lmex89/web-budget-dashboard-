from typing import Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    user_name: str
    created_at: str

    model_config = {"from_attributes": True}
