from fastapi import HTTPException

from app.core.deps import db_dependency, user_dependency
from app.core.security import bcrypt_context
from app.domain.user.models import User
from app.domain.user.schemas import ChangeUserPasswordRequest


def change_password_action(
    auth_user: user_dependency, db: db_dependency, request: ChangeUserPasswordRequest
):
    user = db.query(User).filter(User.id == auth_user.get("user_id")).first()

    if not bcrypt_context.verify(request.password, user.password):  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if bcrypt_context.hash(request.password) == user.password:  # type: ignore
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )

    user.password = bcrypt_context.hash(request.password)  # type: ignore
    db.commit()
