"""Email API schemas."""
from pydantic import BaseModel, EmailStr


class SendTestEmailRequest(BaseModel):
    """Payload for the admin-only email smoke test."""

    to: EmailStr
    subject: str | None = None
