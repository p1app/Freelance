import pytest

from core.enums import RoleEnum  # type: ignore
from core.security import JWTUser, create_access_token  # type: ignore

access_token_client = create_access_token(JWTUser(id=1, role=RoleEnum.CLIENT))
access_token_freelancer = create_access_token(JWTUser(id=2, role=RoleEnum.FREELANCER))
access_token_admin = create_access_token(JWTUser(id=3, role=RoleEnum.ADMIN))


@pytest.mark.parametrize(
    "access_token, expactation_code",
    [
        (access_token_client, 200),
        (access_token_freelancer, 200),
        (access_token_admin, 200),
        ("fake_token", 401),
    ],
)
def test_get_profile_me(access_token, expactation_code, client):
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    print(response.json())
    assert response.status_code == expactation_code


@pytest.mark.parametrize(
    "fullname, access_token, expactation_code",
    [
        ("test_name", access_token_client, 200),
        ("test_name", "fake_token", 401),
        (None, access_token_client, 422),
    ],
)
def test_update_user(fullname, access_token, expactation_code, client):
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"fullname": fullname},
    )
    assert response.status_code == expactation_code
