"""No-op provider used when email delivery is intentionally turned off."""
from loguru import logger

from app.domains.email.models import EmailMessage, EmailSendResult
from app.domains.email.provider import EmailProvider


class DisabledEmailProvider(EmailProvider):
    """Drop messages and report the failure without raising."""

    @property
    def name(self) -> str:
        return "disabled"

    async def send(self, message: EmailMessage) -> EmailSendResult:
        logger.debug(f"Email disabled, dropping message to {message.to}")
        return EmailSendResult(
            success=False,
            provider=self.name,
            error="Email provider is disabled.",
        )
