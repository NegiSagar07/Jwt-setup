from functools import lru_cache

from ..config import settings
from .base import EmailSender
from .smtp import SMTPEmailSender


@lru_cache
def get_email_sender() -> EmailSender:
    if settings.EMAIL_PROVIDER == "smtp":
        return SMTPEmailSender()
    # elif settings.EMAIL_PROVIDER == "ses":
    #     from .ses import SESEmailSender
    #     return SESEmailSender()
    raise ValueError(f"Unknown EMAIL_PROVIDER: {settings.EMAIL_PROVIDER!r}")


async def send_password_reset_otp_email(to_email: str, otp: str) -> None:
    subject = "Your password reset code"
    body = (
        f"Your one-time password reset code is: {otp}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n\n"
        "If you did not request a password reset, you can safely ignore this email."
    )
    await get_email_sender().send(to_email, subject, body)
