"""Per-request tenant (family) context.

Uses a contextvar so the active ``family_id`` is available to any code running
inside the request's async task without threading it through every call
signature. The global SQLAlchemy tenant guard reads this value to inject
``family_id`` predicates into every SELECT on tenant-owned models.

The value is bound in ``get_current_user`` and cleared after each request by
the ``tenant_scope`` dependency (see ``app/dependencies/tenant.py``).
"""
from contextvars import ContextVar

from loguru import logger

_tenant_family_id: ContextVar[str | None] = ContextVar("tenant_family_id", default=None)


def set_tenant_context(family_id: str) -> None:
    """Bind the current task to a family (tenant)."""
    _tenant_family_id.set(family_id)
    logger.debug(f"Tenant context set: family={family_id}")


def get_tenant_context() -> str | None:
    """Return the active family_id for the current task, if any."""
    return _tenant_family_id.get()


def clear_tenant_context() -> None:
    """Reset the tenant context (called at the end of each request)."""
    _tenant_family_id.set(None)
