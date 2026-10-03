"""Unit tests for the provider-agnostic email layer."""
import json

import httpx
import pytest

from app.core.config import Settings
from app.core.exceptions import EmailProviderError
from app.domains.email.models import EmailMessage, EmailSendResult
from app.domains.email.provider import EmailProvider
from app.domains.services.email_service import EmailService
from app.infrastructure.email.brevo import BREVO_SMTP_EMAIL_URL, BrevoEmailProvider
from app.infrastructure.email.console import ConsoleEmailProvider
from app.infrastructure.email.disabled import DisabledEmailProvider
from app.infrastructure.email.factory import create_email_provider


def _message() -> EmailMessage:
    return EmailMessage(to=["user@example.com"], subject="Hi", html_content="<p>Hello</p>")


class _CapturingProvider(EmailProvider):
    """Test double that records messages instead of sending them."""

    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    @property
    def name(self) -> str:
        return "capture"

    async def send(self, message: EmailMessage) -> EmailSendResult:
        self.messages.append(message)
        return EmailSendResult(success=True, provider=self.name, message_id="1")


class _FailingProvider(EmailProvider):
    """Test double whose upstream call always fails."""

    @property
    def name(self) -> str:
        return "failing"

    async def send(self, message: EmailMessage) -> EmailSendResult:
        raise EmailProviderError(self.name, "upstream down", status_code=500)


async def test_brevo_provider_posts_expected_payload():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["api_key"] = request.headers.get("api-key")
        captured["payload"] = json.loads(request.content)
        return httpx.Response(201, json={"messageId": "<abc@brevo>"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = BrevoEmailProvider(
            api_key="test-key",
            from_email="sender@example.com",
            from_name="Family Budget",
            client=client,
        )
        result = await provider.send(_message())

    assert result.success is True
    assert result.provider == "brevo"
    assert result.message_id == "<abc@brevo>"
    assert captured["url"] == BREVO_SMTP_EMAIL_URL
    assert captured["api_key"] == "test-key"
    assert captured["payload"]["sender"] == {
        "name": "Family Budget",
        "email": "sender@example.com",
    }
    assert captured["payload"]["to"] == [{"email": "user@example.com"}]
    assert captured["payload"]["subject"] == "Hi"
    assert captured["payload"]["htmlContent"] == "<p>Hello</p>"


async def test_brevo_provider_raises_on_rejected_email():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"code": "invalid_parameter", "message": "Sender not valid"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = BrevoEmailProvider(
            api_key="test-key",
            from_email="sender@example.com",
            from_name="Family Budget",
            client=client,
        )
        with pytest.raises(EmailProviderError) as exc_info:
            await provider.send(_message())

    assert exc_info.value.status_code == 400
    assert "Sender not valid" in str(exc_info.value)


async def test_brevo_provider_raises_on_transport_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = BrevoEmailProvider(
            api_key="test-key",
            from_email="sender@example.com",
            from_name="Family Budget",
            client=client,
        )
        with pytest.raises(EmailProviderError) as exc_info:
            await provider.send(_message())

    assert exc_info.value.status_code is None
    assert "HTTP request failed" in str(exc_info.value)


async def test_service_returns_failed_result_when_provider_raises():
    result = await EmailService(_FailingProvider()).send(_message())

    assert result.success is False
    assert result.provider == "failing"
    assert "upstream down" in result.error


async def test_welcome_email_renders_and_escapes_user_input():
    provider = _CapturingProvider()

    await EmailService(provider).send_welcome_email(
        to="ana@example.com",
        full_name="Ana <script>alert(1)</script>",
        family_name="Lopez",
    )

    message = provider.messages[0]
    assert message.to == ["ana@example.com"]
    assert "Ana" in message.subject
    assert "<script>" not in message.html_content
    assert "&lt;script&gt;" in message.html_content
    assert "Lopez" in message.html_content


async def test_invitation_email_includes_credentials():
    provider = _CapturingProvider()

    await EmailService(provider).send_family_invitation(
        to="luis@example.com",
        full_name="Luis",
        family_name="Lopez",
        temporary_password="S3cret!",
        invited_by="Ana",
    )

    message = provider.messages[0]
    assert message.to == ["luis@example.com"]
    assert "S3cret!" in message.html_content
    assert "S3cret!" in message.text_content
    assert "Luis" in message.html_content
    assert "Ana" in message.html_content


def test_factory_defaults_to_disabled():
    provider = create_email_provider(Settings(_env_file=None))

    assert isinstance(provider, DisabledEmailProvider)


def test_factory_builds_console_provider():
    provider = create_email_provider(Settings(_env_file=None, EMAIL_PROVIDER="console"))

    assert isinstance(provider, ConsoleEmailProvider)


def test_factory_unknown_provider_falls_back_to_disabled():
    provider = create_email_provider(Settings(_env_file=None, EMAIL_PROVIDER="sendgrid"))

    assert isinstance(provider, DisabledEmailProvider)


@pytest.mark.parametrize("missing", ["key", "sender"])
def test_factory_brevo_requires_key_and_sender(missing):
    overrides = {"EMAIL_PROVIDER": "brevo", "EMAIL_API_KEY": "k", "EMAIL_FROM_EMAIL": "s@e.com"}
    overrides["EMAIL_API_KEY" if missing == "key" else "EMAIL_FROM_EMAIL"] = ""

    provider = create_email_provider(Settings(_env_file=None, **overrides))

    assert isinstance(provider, DisabledEmailProvider)


def test_factory_builds_brevo_with_generic_key():
    provider = create_email_provider(
        Settings(
            _env_file=None,
            EMAIL_PROVIDER="brevo",
            EMAIL_API_KEY="generic-key",
            EMAIL_FROM_EMAIL="sender@example.com",
        )
    )

    assert isinstance(provider, BrevoEmailProvider)


@pytest.mark.parametrize("legacy_field", ["BREVO_API_KEY", "APIKEY_BREVO", "APIKYE_BREVO"])
def test_factory_accepts_legacy_brevo_key_names(legacy_field):
    provider = create_email_provider(
        Settings(
            _env_file=None,
            EMAIL_PROVIDER="brevo",
            EMAIL_FROM_EMAIL="sender@example.com",
            **{legacy_field: "legacy-key"},
        )
    )

    assert isinstance(provider, BrevoEmailProvider)
