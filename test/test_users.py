from core.dependencies import get_db
from core.jwt import get_current_user
from fastapi import status
from main import app

from test.utils import (
    client,
    override_get_current_user,
    override_get_db,
    test_user_instance,
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user(test_user_instance):
    response = client.get("/users")

    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    assert res["username"] == "Testuser"
    assert res["email"] == "test@email.com"
    assert res["role"] == "admin"


def test_change_password_success(test_user_instance):
    response = client.put(
        "/users/change_password",
        json={"password": "testpassword", "new_password": "newpassword"},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED


def test_change_password_invalid(test_user_instance):
    response = client.put(
        "/users/change_password",
        json={"password": "wrongpassword", "new_password": "newpassword"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}
