import pytest
from django.db import IntegrityError

from accounts.models import User


@pytest.mark.django_db
def test_create_user_normalizes_email_and_hashes_password():
    user = User.objects.create_user(email="Person@Example.COM", password="s3cret-pass")

    assert user.email == "Person@example.com"
    assert user.password != "s3cret-pass"
    assert user.check_password("s3cret-pass")


@pytest.mark.django_db
def test_create_superuser_sets_staff_and_superuser_flags():
    user = User.objects.create_superuser(email="admin@example.com", password="s3cret-pass")

    assert user.is_staff is True
    assert user.is_superuser is True


def test_create_user_without_email_raises():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="s3cret-pass")


@pytest.mark.django_db
def test_email_is_unique():
    User.objects.create_user(email="dup@example.com", password="s3cret-pass")

    with pytest.raises(IntegrityError):
        User.objects.create_user(email="dup@example.com", password="another-pass")
