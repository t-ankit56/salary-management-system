import pytest

from accounts.models import User
from employees.models import Country, Department, Role


@pytest.fixture
def user(db):
    return User.objects.create_user(email="hr@example.com", password="s3cret-pass")


@pytest.fixture
def reference_data(db):
    return {
        "department": Department.objects.create(name="Engineering"),
        "role": Role.objects.create(name="Manager"),
        "country": Country.objects.create(name="India"),
    }
