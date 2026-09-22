from fastapi import HTTPException

from app.core.deps import db_dependency, user_dependency
from app.domain.user.models import User
from app.domain.user.schemas import UpdateUserRequest


def update_me_action(
    request: UpdateUserRequest, auth_user: user_dependency, db: db_dependency
):
    user_model = db.query(User).filter(User.id == auth_user.get("user_id")).first()

    if request.username:
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user and existing_user.id != user_model.id:  # type: ignore
            raise HTTPException(status_code=409, detail="Username already taken")
        user_model.username = request.username  # type: ignore

    if request.email:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user and existing_user.id != user_model.id:  # type: ignore
            raise HTTPException(status_code=409, detail="Email already taken")
        user_model.email = request.email  # type: ignore

    db.add(user_model)
    db.commit()
