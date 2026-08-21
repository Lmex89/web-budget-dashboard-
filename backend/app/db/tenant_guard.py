"""Global multi-tenant isolation guard.

Registers a ``do_orm_execute`` listener that injects ``with_loader_criteria``
predicates (``family_id == <active family>``) into every SELECT on
tenant-owned models. This is a defense-in-depth safety net: even a query that
forgets to scope by family is filtered automatically whenever the tenant
context is set.

Enabled via ``ENABLE_GLOBAL_TENANT_GUARD``. The ``User`` model is intentionally
excluded because auth flows (login/register, global email uniqueness) must be
able to read users across families. ``Installment`` and ``AuditLog`` have no
``family_id`` column and are reached only through tenant-owned relations, so
they are excluded too.
"""
from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria

from loguru import logger
from app.core.config import settings
from app.core.tenant import get_tenant_context
from app.models import Expense, Category, CreditCard, Debt

_TENANT_MODELS = (Expense, Category, CreditCard, Debt)


def _apply_tenant_guard(execute_state) -> None:
    """Inject family predicates into tenant-owned SELECT statements."""
    if not settings.ENABLE_GLOBAL_TENANT_GUARD:
        return
    if not execute_state.is_select:
        return
    if execute_state.is_column_load or execute_state.is_relationship_load:
        return

    family_id = get_tenant_context()
    if family_id is None:
        return

    options = [
        with_loader_criteria(
            model,
            lambda cls: cls.family_id == family_id,
            include_aliases=True,
        )
        for model in _TENANT_MODELS
    ]
    execute_state.statement = execute_state.statement.options(*options)
    logger.debug(
        f"Tenant guard applied: family={family_id}, "
        f"models={[m.__name__ for m in _TENANT_MODELS]}"
    )


def install_tenant_guard() -> None:
    """Register the global tenant guard listener (idempotent).

    Listens on the underlying ORM ``Session`` class; async sessions dispatch
    ORM ``do_orm_execute`` events to it.
    """
    from sqlalchemy.orm import Session

    if not event.contains(Session, "do_orm_execute", _apply_tenant_guard):
        event.listen(Session, "do_orm_execute", _apply_tenant_guard)
        logger.info("Global tenant guard registered")
