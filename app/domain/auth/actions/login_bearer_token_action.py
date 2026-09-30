from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.sql.annotation import Annotated

from app.core.deps import db_dependency
from app.core.security import create_access_token
from app.core.settings import settings
from app.domain.auth.helpers.authenticate_user import authenticate_user


def login_bearer_token_action(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):  # add response type add some point
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
