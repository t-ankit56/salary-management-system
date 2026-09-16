import pytest

from accounts.models import User
from employees.models import Country, Department, Employee, Role


@pytest.fixture
def user(db):
    return User.objects.create_user(email="hr@example.com", password="s3cret-pass")


@pytest.fixture
def employee(db):
    department = Department.objects.create(name="Engineering")
    role = Role.objects.create(name="Manager")
    country = Country.objects.create(name="India")
    return Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        department=department,
        role=role,
        country=country,
        hire_date="2020-01-01",
    )


@pytest.fixture
def other_employee(db):
    department = Department.objects.create(name="Sales")
    role = Role.objects.create(name="Associate")
    country = Country.objects.create(name="USA")
    return Employee.objects.create(
        employee_code="E002",
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        department=department,
        role=role,
        country=country,
        hire_date="2020-01-01",
    )
