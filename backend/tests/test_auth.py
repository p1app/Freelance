import pytest

from core.enums import RoleEnum  # type: ignore
from core.security import JWTUser, create_access_token  # type: ignore

some_access_token = create_access_token(JWTUser(id=1, role=RoleEnum.CLIENT))


@pytest.mark.parametrize(
    "username, email, role, fullname, password, expactation_code",
    [
        (
            "test_client",
            "client@gmail.com",
            "client",
            "user",
            "test_pass",
            201,
        ),
        (
            "test_freelancer",
            "freelancer@gmail.com",
            "freelancer",
            "user",
            "test_pass",
            201,
        ),
        (
            "test_admin",
            "admin@gmail.com",
            "admin",
            "user",
            "test_pass",
            201,
        ),
        (
            "test_client",
            "user@gmail.com",
            "client",
            "user",
            "test_pass",
            400,
        ),
        (
            "test_user",
            "client@gmail.com",
            "client",
            "user",
            "test_pass",
            400,
        ),
        (
            "test_user1",
            "example1@gmail.com",
            "client",
            "user",
            "1234",  # проваленный пароль
            422,
        ),
    ],
)
def test_register(username, email, role, fullname, password, expactation_code, client):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "role": role,
            "fullname": fullname,
            "password": password,
        },
    )
    if expactation_code == 201:
        assert response.json()["token_type"] == "bearer"
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
    assert response.status_code == expactation_code


@pytest.mark.parametrize(
    "username, password, expactation_code",
    [("test_client", "test_pass", 200), ("test_user", "password", 401)],
)
def test_login(username, password, expactation_code, client):
    response = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    if expactation_code == 201:
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
    assert response.status_code == expactation_code


@pytest.mark.parametrize(
    "token, expactation_code", [(some_access_token, 200), ("fake_token", 401)]
)
def test_logout(token, client, expactation_code):
    response = client.post(
        "/auth/logout/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == expactation_code
