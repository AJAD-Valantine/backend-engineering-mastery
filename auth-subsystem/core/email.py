import smtplib
from email.message import EmailMessage

from core.config import Settings
from fastapi import HTTPException


class EmailManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _send(self, to_email: str, subject: str, content: str) -> None:
        """Internal helper to handle SMTP connection and exception handling."""
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "noreply@library.com"
        msg["To"] = to_email
        msg.set_content(content)

        try:
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port
            ) as server:
                server.send_message(msg)
        except smtplib.SMTPException:
            raise HTTPException(
                status_code=500, detail=f"Failed to send email: {subject}"
            )

    def send_reset_email(self, to_email: str, raw_token: str) -> None:
        reset_url = f"{self.settings.frontend_url}/reset-password?token={raw_token}"
        content = f"Click to reset your password: {reset_url}"
        self._send(to_email=to_email, subject="Password Reset", content=content)

    def send_verification_email(self, to_email: str, raw_token: str) -> None:
        verify_url = f"{self.settings.frontend_url}/verify-email?token={raw_token}"
        content = f"Click to verify your email: {verify_url}"
        self._send(to_email=to_email, subject="Email Verification", content=content)
