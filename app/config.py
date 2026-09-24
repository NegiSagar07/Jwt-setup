from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB (Atlas) connection
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "jwt_setup"

    # Security settings for JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Which email backend app/email/__init__.py should use. "smtp" today,
    # "ses" once that backend is wired in (see app/email/ses.py).
    EMAIL_PROVIDER: str = "smtp"

    # SMTP (for forgot-password OTP emails). Optional at the Settings level
    # so a non-smtp EMAIL_PROVIDER doesn't require these — SMTPEmailSender
    # itself validates they're set when it's actually the active provider.
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "App"

    # AWS SES (uncomment / fill in when switching EMAIL_PROVIDER to "ses")
    # AWS_REGION: Optional[str] = None
    # AWS_ACCESS_KEY_ID: Optional[str] = None
    # AWS_SECRET_ACCESS_KEY: Optional[str] = None

    OTP_EXPIRE_MINUTES: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
