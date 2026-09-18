import smtplib
from email.message import EmailMessage

from fastapi import HTTPException

from app.core.config import Settings

settings = Settings()  # type: ignore

def send_reset_email(to_email: str, raw_token: str) -> None:

    reset_url: str = f"{settings.frontend_url}/reset-password?token={raw_token}"

    content: str = f"Click to reset: {reset_url}"

    msg: EmailMessage = EmailMessage()

    msg["Subject"] = "Password Reset"
    msg["From"] = "noreply@library.com"
    msg["To"] = to_email

    msg.set_content(content)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.send_message(msg)

    except smtplib.SMTPException:
        raise HTTPException(status_code=500, detail="Failed to send password reset email.")

def send_verification_email(to_email: str, raw_token: str) -> None:

    reset_url: str = f"{settings.frontend_url}/verify-email?token={raw_token}"

    content: str = f"Click to verify: {reset_url}"

    msg: EmailMessage = EmailMessage()

    msg["Subject"] = "Email Verification"
    msg["From"] = "noreply@library.com"
    msg["To"] = to_email

    msg.set_content(content)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.send_message(msg)

    except smtplib.SMTPException:
        raise HTTPException(status_code=500, detail="Failed to send email verification email.")
