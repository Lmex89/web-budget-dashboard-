"""Admin-only email diagnostics endpoints."""
from fastapi import APIRouter, Depends

from app.dependencies.auth import require_admin
from app.dependencies.email import get_email_service
from app.domains.email.models import EmailMessage
from app.domains.services.email_service import EmailService
from app.models import User
from app.schemas.common import BaseResponse
from app.schemas.email import SendTestEmailRequest

router = APIRouter(prefix="/emails", tags=["Email"])


@router.post("/test", response_model=BaseResponse)
async def send_test_email(
    data: SendTestEmailRequest,
    email_service: EmailService = Depends(get_email_service),
    _admin: User = Depends(require_admin),
):
    """Send a diagnostic email through the configured provider.

    Returns the provider outcome in the payload instead of an error status so
    admins can read the upstream rejection reason while validating setup.
    """
    result = await email_service.send(
        EmailMessage(
            to=[data.to],
            subject=data.subject or "Family Budget email test",
            html_content="<p>This is a test email from Family Budget.</p>",
            text_content="This is a test email from Family Budget.",
        )
    )
    return BaseResponse(
        data={
            "success": result.success,
            "provider": result.provider,
            "message_id": result.message_id,
            "error": result.error,
        }
    )
