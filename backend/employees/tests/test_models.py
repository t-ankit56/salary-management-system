import pytest
from django.db import IntegrityError

from employees.models import Country, Department, Role


@pytest.mark.django_db
def test_department_name_is_unique():
    Department.objects.create(name="Engineering")

    with pytest.raises(IntegrityError):
        Department.objects.create(name="Engineering")


@pytest.mark.django_db
def test_role_name_is_unique():
    Role.objects.create(name="Manager")

    with pytest.raises(IntegrityError):
        Role.objects.create(name="Manager")


@pytest.mark.django_db
def test_country_name_is_unique():
    Country.objects.create(name="India")

    with pytest.raises(IntegrityError):
        Country.objects.create(name="India")
