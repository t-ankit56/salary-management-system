import pytest

from employees.models import Country, Department, Role


@pytest.fixture
def reference_data(db):
    return {
        "department": Department.objects.create(name="Engineering"),
        "role": Role.objects.create(name="Manager"),
        "country": Country.objects.create(name="India"),
    }
