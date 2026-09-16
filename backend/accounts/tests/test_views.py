import pytest
from rest_framework.test import APIClient

from accounts.models import User


@pytest.fixture
def user():
    return User.objects.create_user(email="jane@example.com", password="s3cret-pass")


@pytest.mark.django_db
def test_login_with_valid_credentials_establishes_session(user):
    client = APIClient()

    response = client.post(
        "/api/auth/login/", {"email": "jane@example.com", "password": "s3cret-pass"}
    )

    assert response.status_code == 200
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_login_with_invalid_credentials_returns_401(user):
    client = APIClient()

    response = client.post(
        "/api/auth/login/", {"email": "jane@example.com", "password": "wrong-pass"}
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_me_returns_current_user_when_authenticated(user):
    client = APIClient()
    client.login(email="jane@example.com", password="s3cret-pass")

    response = client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["email"] == "jane@example.com"


@pytest.mark.django_db
def test_me_returns_403_when_not_authenticated():
    client = APIClient()

    response = client.get("/api/auth/me/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_logout_ends_session(user):
    client = APIClient()
    client.login(email="jane@example.com", password="s3cret-pass")

    response = client.post("/api/auth/logout/")

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
