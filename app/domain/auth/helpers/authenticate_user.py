from sqlalchemy import or_

from app.core.security import verify_password
from app.domain.user.models import User


def authenticate_user(username_email: str, password: str, db) -> User | bool:
    user = (
        db.query(User)
        .filter(
            or_(User.username == username_email, User.email == username_email)
        )  # email can be username or email
        .first()
    )
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
