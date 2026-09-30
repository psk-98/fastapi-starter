from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import db_dependency
from app.domain.auth.actions.create_user_action import create_user_action
from app.domain.auth.actions.forgot_password_action import forgot_password_action
from app.domain.auth.actions.login_bearer_token_action import login_bearer_token_action
from app.domain.auth.actions.reset_password_action import reset_password_action
from app.domain.auth.schemas import TokenResponse
from app.domain.user.schemas import (
    CreateUserRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserResponse,
)

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
    return reset_password_action(request, db)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(request: CreateUserRequest, db: db_dependency):
    return create_user_action(request, db)
