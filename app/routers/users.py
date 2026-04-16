from fastapi import APIRouter, HTTPException, status

from app.core.deps import db_dependency, user_dependency
from app.core.security import bcrypt_context
from app.models.user import User
from app.schema.users import ChangeUserPasswordRequest, UpdateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_auth_user(auth_user: user_dependency, db: db_dependency):

    return db.query(User).filter(User.id == auth_user.get("user_id")).first()


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
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


@router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
def update_auth_user(
    request: UpdateUserRequest, auth_user: user_dependency, db: db_dependency
):
    user_model = db.query(User).filter(User.id == auth_user.get("user_id")).first()

    if request.username:
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user and existing_user.id != auth_user.id:  # type: ignore
            raise HTTPException(status_code=409, detail="Username already taken")
        user_model.username = request.username  # type: ignore

    if request.email:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user and existing_user.id != auth_user.id:  # type: ignore
            raise HTTPException(status_code=409, detail="Email already taken")
        user_model.email = request.email  # type: ignore

    db.add(user_model)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_auth_user(auth_user: user_dependency, db: db_dependency):
    db.query(User).filter(User.id == auth_user.get("user_id")).delete()
    db.commit()
