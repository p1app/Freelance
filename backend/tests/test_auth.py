import pytest


@pytest.mark.parametrize(
    "username, email, role, fullname, password, expactation_code",
    [
        (
            "p1app",
            "example@gmail.com",
            "client",
            "user",
            "123456",
            201,
        ),
        (
            "p1app",
            "example@gmail.com",
            "client",
            "user",
            "1234",
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
