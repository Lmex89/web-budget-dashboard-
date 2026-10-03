"""Console email provider that logs messages instead of sending them.

Used by ``EMAIL_PROVIDER=console`` for local development.
"""
from loguru import logger

from app.domains.email.models import EmailMessage, EmailSendResult
from app.domains.email.provider import EmailProvider


class ConsoleEmailProvider(EmailProvider):
    """Development provider: log the message and report success."""

    @property
    def name(self) -> str:
        return "console"

    async def send(self, message: EmailMessage) -> EmailSendResult:
        logger.info(f"[console-email] to={message.to} subject={message.subject!r}")
        logger.debug(f"[console-email] html={message.html_content}")
        return EmailSendResult(success=True, provider=self.name, message_id="console")
