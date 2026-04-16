from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import db_dependency
from app.core.security import create_access_token, hash_password, verify_password
from app.core.settings import settings
from app.models.user import User
from app.schema.users import CreateUserRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post(
    "/login/access_token", response_model=TokenResponse, status_code=status.HTTP_200_OK
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


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(request: CreateUserRequest, db: db_dependency):
    request_data = request.model_dump()
    request_data["password"] = hash_password(request.password)
    create_user_model = User(**request_data)
    db.add(create_user_model)
    db.commit()

    return create_user_model
