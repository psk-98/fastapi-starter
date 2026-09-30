from datetime import UTC, datetime, timedelta

from app.core.deps import db_dependency
from app.core.security import generate_reset_token, hash_reset_token
from app.core.settings import settings
from app.domain.auth.models import PasswordResetToken
from app.domain.user.models import User
from app.domain.user.schemas import ForgotPasswordRequest
from app.tasks import send_password_reset_email


def forgot_password_action(request: ForgotPasswordRequest, db: db_dependency):
    user = db.query(User).filter(User.email == request.email).first()

    if user:
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id
        ).delete()

        token = generate_reset_token()
        token_hash = hash_reset_token(token)
        expires_at = datetime.now(UTC) + timedelta(  # change for your timezone
            minutes=settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES
        )

        reset_token = PasswordResetToken(
            user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )

        db.add(reset_token)
        db.commit()

        send_password_reset_email.apply_async(args=[user.email, user.username, token])  # type: ignore[prop-decorator]

    return {
        "message": "If an account exists with this email, you will receive password reset instructions.",
    }
