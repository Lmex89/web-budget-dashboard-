"""Value objects for provider-agnostic email delivery."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    """A single outbound email, independent of any provider API."""

    to: list[str]
    subject: str
    html_content: str
    text_content: str | None = None
    reply_to: str | None = None


@dataclass(frozen=True)
class EmailSendResult:
    """Outcome of a provider send attempt.

    Failures are represented as data (not exceptions) so callers can decide
    whether a notification failure should surface.
    """

    success: bool
    provider: str
    message_id: str | None = None
    error: str | None = None
