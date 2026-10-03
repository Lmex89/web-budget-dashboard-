"""Brevo (formerly Sendinblue) transactional email adapter.

Uses Brevo's REST API directly through ``httpx`` (already a runtime
dependency) instead of the official ``sib-api-v3-sdk``, which is synchronous
and would block the event loop. Only this module knows about Brevo.
"""
import httpx
from loguru import logger

from app.core.exceptions import EmailProviderError
from app.domains.email.models import EmailMessage, EmailSendResult
from app.domains.email.provider import EmailProvider

BREVO_SMTP_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
DEFAULT_TIMEOUT_SECONDS = 10.0


class BrevoEmailProvider(EmailProvider):
    """Send transactional email through Brevo's ``POST /v3/smtp/email``."""

    def __init__(
        self,
        api_key: str,
        from_email: str,
        from_name: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        client: httpx.AsyncClient | None = None,
    ):
        self._api_key = api_key
        self._from_email = from_email
        self._from_name = from_name
        self._timeout = timeout
        # Injected by tests (MockTransport); otherwise a client per send.
        self._client = client

    @property
    def name(self) -> str:
        return "brevo"

    def _build_payload(self, message: EmailMessage) -> dict:
        """Translate the generic message into Brevo's payload shape."""
        payload: dict = {
            "sender": {"name": self._from_name, "email": self._from_email},
            "to": [{"email": address} for address in message.to],
            "subject": message.subject,
            "htmlContent": message.html_content,
        }
        if message.text_content:
            payload["textContent"] = message.text_content
        if message.reply_to:
            payload["replyTo"] = {"email": message.reply_to}
        return payload

    async def send(self, message: EmailMessage) -> EmailSendResult:
        """Send an email through Brevo.

        Raises:
            EmailProviderError: On timeout, transport failure, or a non-2xx
                response from Brevo.
        """
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.post(
                BREVO_SMTP_EMAIL_URL,
                headers={
                    "api-key": self._api_key,
                    "accept": "application/json",
                    "content-type": "application/json",
                },
                json=self._build_payload(message),
            )
        except httpx.HTTPError as exc:
            raise EmailProviderError(self.name, f"HTTP request failed: {exc}") from exc
        finally:
            if self._client is None:
                await client.aclose()

        if response.status_code >= 400:
            # Brevo error payloads look like {"code": "...", "message": "..."}.
            try:
                detail = response.json().get("message", response.text)
            except ValueError:
                detail = response.text
            logger.warning(f"Brevo rejected email: status={response.status_code}, detail={detail}")
            raise EmailProviderError(self.name, str(detail), status_code=response.status_code)

        try:
            data = response.json()
        except ValueError:
            data = {}
        return EmailSendResult(success=True, provider=self.name, message_id=data.get("messageId"))
