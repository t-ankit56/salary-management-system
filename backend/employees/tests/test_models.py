import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from employees.models import Country, Department, Employee, Role


def _create_employee(department, role, country, **overrides):
    defaults = {
        "employee_code": "E001",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "department": department,
        "role": role,
        "country": country,
        "hire_date": "2024-01-01",
    }
    defaults.update(overrides)
    return Employee.objects.create(**defaults)


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


def test_employee_code_is_unique(reference_data):
    _create_employee(**reference_data, employee_code="E001", email="a@example.com")

    with pytest.raises(IntegrityError):
        _create_employee(**reference_data, employee_code="E001", email="b@example.com")


def test_employee_email_is_unique(reference_data):
    _create_employee(**reference_data, employee_code="E001", email="dup@example.com")

    with pytest.raises(IntegrityError):
        _create_employee(**reference_data, employee_code="E002", email="dup@example.com")


def test_department_in_use_cannot_be_deleted(reference_data):
    _create_employee(**reference_data)

    with pytest.raises(ProtectedError):
        reference_data["department"].delete()
