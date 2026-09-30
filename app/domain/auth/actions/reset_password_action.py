from datetime import UTC, datetime

from fastapi import HTTPException

from app.core.deps import db_dependency
from app.core.security import hash_password, hash_reset_token
from app.domain.auth.models import PasswordResetToken
from app.domain.user.models import User
from app.domain.user.schemas import ResetPasswordRequest


def reset_password_action(request: ResetPasswordRequest, db: db_dependency):
    reset_token_instance = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_reset_token(request.token))
        .first()
    )

    if not reset_token_instance:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if reset_token_instance.expires_at < datetime.now(UTC):
        db.delete(reset_token_instance)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == reset_token_instance.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.password = hash_password(request.password)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
    db.add(user)
    db.commit()

    return {
        "message": "Password reset successfully. You can now log in with your new password.",
    }
