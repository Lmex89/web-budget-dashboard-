"""Build the configured email provider from application settings."""
from loguru import logger

from app.core.config import Settings, settings
from app.domains.email.provider import EmailProvider
from app.infrastructure.email.brevo import BrevoEmailProvider
from app.infrastructure.email.console import ConsoleEmailProvider
from app.infrastructure.email.disabled import DisabledEmailProvider


def create_email_provider(config: Settings | None = None) -> EmailProvider:
    """Return the EmailProvider selected by ``EMAIL_PROVIDER``.

    Misconfiguration (unknown name, missing Brevo key or sender) falls back to
    the disabled provider with a warning, so a typo can never crash the app or
    send mail through the wrong backend.
    """
    config = config or settings
    provider = config.EMAIL_PROVIDER.strip().lower()

    if provider == "console":
        return ConsoleEmailProvider()

    if provider == "brevo":
        if not config.resolved_email_api_key or not config.EMAIL_FROM_EMAIL:
            logger.warning(
                "EMAIL_PROVIDER=brevo requires an API key and EMAIL_FROM_EMAIL; email disabled."
            )
            return DisabledEmailProvider()
        return BrevoEmailProvider(
            api_key=config.resolved_email_api_key,
            from_email=config.EMAIL_FROM_EMAIL,
            from_name=config.EMAIL_FROM_NAME,
        )

    if provider != "disabled":
        logger.warning(f"Unknown EMAIL_PROVIDER '{config.EMAIL_PROVIDER}', email disabled.")
    return DisabledEmailProvider()
