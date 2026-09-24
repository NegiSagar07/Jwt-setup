"""Amazon SES email backend — not wired in yet.

To switch to SES later:
1. `pip install aioboto3` (or `boto3` + run send_email in a thread pool)
   and add it to requirements.txt.
2. Add AWS_REGION / AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY (or rely on
   the default AWS credential chain / IAM role) to config.py.
3. Uncomment SESEmailSender below and fill in the send_email call.
4. In app/email/__init__.py, register "ses" -> SESEmailSender in
   get_email_sender(), and set EMAIL_PROVIDER=ses in .env.

No other file needs to change — router/auth.py only calls
send_password_reset_otp_email(), which is provider-agnostic.
"""

# import aioboto3
#
# from ..config import settings
# from .base import EmailSender
#
#
# class SESEmailSender(EmailSender):
#     async def send(self, to_email: str, subject: str, body: str) -> None:
#         session = aioboto3.Session()
#         async with session.client("ses", region_name=settings.AWS_REGION) as ses:
#             await ses.send_email(
#                 Source=f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>",
#                 Destination={"ToAddresses": [to_email]},
#                 Message={
#                     "Subject": {"Data": subject},
#                     "Body": {"Text": {"Data": body}},
#                 },
#             )
