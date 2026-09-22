from fastapi import APIRouter, HTTPException, status

from app.core.deps import db_dependency, user_dependency
from app.core.security import bcrypt_context
from app.domain.user.actions.change_password_action import change_password_action
from app.domain.user.actions.update_me_action import update_me_action
from app.domain.user.models import User
from app.domain.user.schemas import (
    ChangeUserPasswordRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_auth_user(auth_user: user_dependency, db: db_dependency):
    return db.query(User).filter(User.id == auth_user.get("user_id")).first()


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    auth_user: user_dependency, db: db_dependency, request: ChangeUserPasswordRequest
):
    change_password_action(auth_user, db, request)


@router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
def update_me(
    request: UpdateUserRequest, auth_user: user_dependency, db: db_dependency
):
    update_me_action(request, auth_user, db)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_auth_user(auth_user: user_dependency, db: db_dependency):
    db.query(User).filter(User.id == auth_user.get("user_id")).delete()
    db.commit()
