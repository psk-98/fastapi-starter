import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.settings import settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
) -> str:
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": username, "id": user_id, "role": role, "exp": expires}

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password(entered_password: str, user_password: str):
    return bcrypt_context.verify(entered_password, user_password)


def hash_password(password: str):
    return bcrypt_context.hash(password)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
