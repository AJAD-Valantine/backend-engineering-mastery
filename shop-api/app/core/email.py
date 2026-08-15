import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_password_reset_email(to_email: str, token: str) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = "Reset your password"

    message.set_content(
        f"You requested a password reset.\n\n"
        f"Your reset token is: {token}\n\n"
        f"This token expires in {settings.reset_token_expire_minutes} minutes."
    )

    with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
        if settings.mail_use_tls:
            server.starttls()
        server.login(settings.mail_username, settings.mail_password.get_secret_value())
        server.send_message(message)