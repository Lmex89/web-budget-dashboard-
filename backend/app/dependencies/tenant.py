"""Request-scoped tenant context lifecycle dependency."""
from app.core.tenant import clear_tenant_context


async def tenant_scope():
    """Clear the tenant context after the request completes.

    Registered as a global dependency so the per-task contextvar never leaks
    into the next request handled by the same task.
    """
    try:
        yield
    finally:
        clear_tenant_context()
