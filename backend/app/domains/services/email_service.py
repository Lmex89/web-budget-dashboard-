"""Provider-agnostic email notifications with application templates.

Rendering stays here so routes stay thin. Delivery failures are downgraded to
a failed ``EmailSendResult`` because notifications must never fail the request
that triggered them.
"""
import html

from loguru import logger

from app.core.config import settings
from app.core.exceptions import EmailProviderError
from app.domains.email.models import EmailMessage, EmailSendResult
from app.domains.email.provider import EmailProvider


class EmailService:
    """Render and send application emails through an injected provider."""

    def __init__(self, provider: EmailProvider):
        self.provider = provider

    @property
    def provider_name(self) -> str:
        """Return the configured provider identifier."""
        return self.provider.name

    async def send(self, message: EmailMessage) -> EmailSendResult:
        """Deliver a message, converting provider failures into a result.

        Notification delivery is best-effort: instead of raising, provider
        errors are logged and returned as ``success=False`` so callers can
        treat email as a side effect of their main operation.
        """
        try:
            result = await self.provider.send(message)
        except EmailProviderError as exc:
            logger.exception(f"Email delivery failed via {self.provider.name}")
            return EmailSendResult(success=False, provider=self.provider.name, error=str(exc))

        if result.success:
            logger.info(
                f"Email sent via {self.provider.name}: to={message.to}, subject={message.subject!r}"
            )
        else:
            logger.warning(f"Email skipped via {self.provider.name}: {result.error}")
        return result

    async def send_welcome_email(
        self,
        *,
        to: str,
        full_name: str,
        family_name: str,
    ) -> EmailSendResult:
        """Send the welcome email after a user registers a new family."""
        safe_name = html.escape(full_name)
        body = (
            f"<p>Hi {safe_name},</p>"
            f"<p>Your family <strong>{html.escape(family_name)}</strong> is ready. "
            "Track expenses, budgets, and debts from one place.</p>"
        )
        return await self.send(
            EmailMessage(
                to=[to],
                subject=f"Welcome to Family Budget, {full_name}!",
                html_content=self._layout("Welcome to Family Budget", body),
                text_content=(
                    f"Hi {full_name},\n\nYour family {family_name} is ready. "
                    "Open Family Budget to get started."
                ),
            )
        )

    async def send_family_invitation(
        self,
        *,
        to: str,
        full_name: str,
        family_name: str,
        temporary_password: str,
        invited_by: str,
    ) -> EmailSendResult:
        """Send a family member their login email and temporary password.

        The invitation includes the admin-set password because the app has no
        password-reset flow yet; remove it once self-service reset exists.
        """
        safe_name = html.escape(full_name)
        body = (
            f"<p>Hi {safe_name},</p>"
            f"<p><strong>{html.escape(invited_by)}</strong> added you to the "
            f"<strong>{html.escape(family_name)}</strong> family on Family Budget.</p>"
            "<p>Sign in with your email and this temporary password:</p>"
            f"<p>Email: <strong>{html.escape(to)}</strong><br>"
            f"Temporary password: <code>{html.escape(temporary_password)}</code></p>"
        )
        return await self.send(
            EmailMessage(
                to=[to],
                subject=f"You were added to {family_name} on Family Budget",
                html_content=self._layout("You are invited", body),
                text_content=(
                    f"Hi {full_name},\n\n{invited_by} added you to the {family_name} family.\n"
                    f"Email: {to}\nTemporary password: {temporary_password}"
                ),
            )
        )

    @staticmethod
    def _layout(title: str, body_html: str) -> str:
        """Wrap body HTML in the shared email shell with an optional CTA."""
        base_url = settings.APP_BASE_URL.strip().rstrip("/")
        cta = ""
        if base_url:
            cta = (
                '<p style="margin:24px 0;">'
                f'<a href="{html.escape(base_url)}" '
                'style="background:#1f2937;color:#ffffff;padding:10px 18px;'
                'border-radius:6px;text-decoration:none;">Open Family Budget</a></p>'
            )
        return (
            '<!doctype html><html><body style="font-family:Arial,Helvetica,sans-serif;'
            'color:#1f2937;line-height:1.5;">'
            f"<h2>{html.escape(title)}</h2>{body_html}{cta}"
            '<p style="color:#6b7280;font-size:12px;">Family Budget</p>'
            "</body></html>"
        )
