"""Audit log API endpoints.

Thin route handlers — delegates query logic to AuditLogService.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from loguru import logger

from app.dependencies.auth import get_current_active_user, require_roles
from app.dependencies.services import get_audit_log_service
from app.domains.services.audit_log_service import AuditLogService
from app.schemas.common import PaginatedResponse
from app.models import User, UserRole

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("", response_model=PaginatedResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuditLogService = Depends(get_audit_log_service),
):
    logger.info(f"GET /audit-logs - user={current_user.id}, page={page}, size={page_size}")
    audit_logs, total = await service.list_by_family(
        family_id=current_user.family_id,
        page=page,
        page_size=page_size,
        entity_type=entity_type,
        action=action,
    )

    return PaginatedResponse(
        data=[
            {
                "id": log.id,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "action": log.action,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "user_name": log.user.full_name if log.user else "Unknown",
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_logs
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )
