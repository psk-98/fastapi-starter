from dataclasses import dataclass
from pathlib import Path
from typing import Any

import emails
from jinja2 import Template

from app.core.settings import settings


@dataclass
class EmailData:
    html_content: str
    plain_text: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email_templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *, email_to: str, subject: str = "", html_content: str = "", plain_text: str
) -> None:
    assert settings.emails_enabled, "No provided configuration for email variables"
    message = emails.Message(  # type: ignore[prop-decorator]
        subject=subject,
        html=html_content,
        text=plain_text,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),  # type: ignore[prop-decorator]
    )

    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
    }
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    response = message.send(to=email_to, smtp=smtp_options)
    print(response)


def generate_password_reset_email(username: str, token: str) -> EmailData:
    subject = f"{settings.PROJECT_NAME} - Password rest for {username}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES // 60,
            "link": link,
        },
    )
    plain_text = f"""Hi {username},

    You requested to reset your password. Click the link below to set a new password:

    {link}

    This link will expire in 1 hour.

    If you didn't request this, you can safely ignore this email.

    Best regards,
    {settings.PROJECT_NAME}
    """

    return EmailData(html_content=html_content, subject=subject, plain_text=plain_text)


def generate_new_account_email(
    email_to: str,
    username: str,
) -> EmailData:
    subject = f"{settings.PROJECT_NAME} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "link": f"{settings.FRONTEND_HOST}/login",
        },
    )
    plain_text = f"""{settings.PROJECT_NAME} - New Account

    Welcome to your new account!

    Go to the Dashboard and use your username: {username}

    {f"{settings.FRONTEND_HOST}/login"}

    """
    return EmailData(html_content=html_content, subject=subject, plain_text=plain_text)


def generate_test_email(email_to: str) -> EmailData:
    subject = f"{settings.PROJECT_NAME} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    plain_text = f"""{settings.PROJECT_NAME}

    Test email for {email_to}
    """
    return EmailData(html_content=html_content, subject=subject, plain_text=plain_text)
