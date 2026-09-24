from email.message import EmailMessage

import aiosmtplib

from ..config import settings
from .base import EmailSender


class SMTPEmailSender(EmailSender):
    def __init__(self) -> None:
        missing = [
            name
            for name in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM_EMAIL")
            if not getattr(settings, name)
        ]
        if missing:
            raise ValueError(f"SMTP email provider is missing settings: {', '.join(missing)}")

    async def send(self, to_email: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
