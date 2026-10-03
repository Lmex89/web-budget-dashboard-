"""Abstract port for transactional email providers."""
from abc import ABC, abstractmethod

from app.domains.email.models import EmailMessage, EmailSendResult


class EmailProvider(ABC):
    """Port implemented by each email backend (Brevo, console, future SMTP)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider identifier used in logs and send results."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> EmailSendResult:
        """Send one transactional email.

        Args:
            message: Provider-agnostic message to deliver.

        Returns:
            The send outcome, including the provider message id when available.

        Raises:
            EmailProviderError: When the upstream API rejects or fails the call.
        """
