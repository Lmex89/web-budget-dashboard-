"""Dependency injection for the email provider and service."""
from functools import lru_cache

from fastapi import Depends

from app.core.config import settings
from app.domains.email.provider import EmailProvider
from app.domains.services.email_service import EmailService
from app.infrastructure.email.factory import create_email_provider


@lru_cache
def get_email_provider() -> EmailProvider:
    """Return the process-wide email provider built from settings."""
    return create_email_provider(settings)


def get_email_service(provider: EmailProvider = Depends(get_email_provider)) -> EmailService:
    """Return an EmailService bound to the configured provider."""
    return EmailService(provider)
