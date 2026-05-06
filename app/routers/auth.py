from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_

from app.core.deps import db_dependency
from app.core.security import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.core.settings import settings
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User

from app.schema.users import (
    CreateUserRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.tasks import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_user(username_email: str, password: str, db) -> User | bool:
    user = (
        db.query(User)
        .filter(or_(User.username == username_email, User.email == username_email))
        .first()
    )
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post(
    "/login/access_token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    description="Login in with your username or email in the username field.",
)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )
    token = create_access_token(
        user.username,  # type: ignore
        user.id,  # type: ignore
        user.role,  # type: ignore
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": token, "token_type": "Bearer"}


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(request: ForgotPasswordRequest, db: db_dependency):
    user = db.query(User).filter(User.email == request.email).first()

    print(user)

    if user:
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id
        ).delete()

        token = generate_reset_token()
        token_hash = hash_reset_token(token)
        expires_at = datetime.now(UTC) + timedelta(
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


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: db_dependency):
    print(len(hash_reset_token(request.token)))

    reset_token_instance = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_reset_token(request.token))
        .first()
    )

    if not reset_token_instance:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    if reset_token_instance.expires_at < datetime.now(UTC):
        db.delete(reset_token_instance)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    user = db.query(User).filter(User.id == reset_token_instance.user_id).first()
    print(reset_token_instance.user.username)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    user.password = hash_password(request.password)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
    db.add(user)
    db.commit()

    return {
        "message": "Password reset successfully. You can now log in with your new password.",
    }


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(request: CreateUserRequest, db: db_dependency):
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=409, detail="Email already taken")

    request_data = request.model_dump()
    request_data["password"] = hash_password(request.password)
    create_user_model = User(**request_data)
    db.add(create_user_model)
    db.commit()

    return create_user_model
