from enum import Enum as PyEnum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, PyEnum):
    user = "user"
    admin = "admin"


class UpdateUserRequest(BaseModel):
    email: str | None
    username: str | None


class ChangeUserPasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=8)

    model_config = {
        "json_schema_extra": {
            "example": {"password": "oldpassword", "new_password": "newpassword"}
        }
    }


class UserResponse(BaseModel):
    email: str
    username: str
    role: UserRole

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "role": "user",
            }
        },
    }


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_active: bool
    role: UserRole

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123",
                "role": "user",
                "is_active": True,
            }
        }
    }


class CurrentUser(BaseModel):
    user: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
