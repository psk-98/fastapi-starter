from celery import Celery

from app.core.settings import settings
from app.utils import generate_password_reset_email, send_email

celery_app = Celery(main="tasks", broker=settings.CELERY_BROKER_URI)


@celery_app.task(name="send_password_reset_email")
def send_password_reset_email(email: str, username: str, token: str) -> None:
    email_data = generate_password_reset_email(username=username, token=token)
    send_email(
        email_to=email,
        subject=email_data.subject,
        html_content=email_data.html_content,
        plain_text=email_data.plain_text,
    )
