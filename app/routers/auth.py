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
from app.domain.auth.actions import forgot_password_action
from app.domain.auth.actions.login_bearer_token_action import login_bearer_token_action
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


@router.post(
    "/login/access_token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    description="Login in with your username or email in the username field.",
)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    return login_bearer_token_action(form_data, db)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(request: ForgotPasswordRequest, db: db_dependency):
    return forgot_password_action(request, db)


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
