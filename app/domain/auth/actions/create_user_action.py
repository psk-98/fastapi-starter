from fastapi import HTTPException

from app.core.deps import db_dependency
from app.core.security import hash_password
from app.domain.user.models import User
from app.domain.user.schemas import CreateUserRequest


def create_user_action(request: CreateUserRequest, db: db_dependency):
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
