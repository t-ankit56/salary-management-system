import pytest

from accounts.models import User
from employees.models import Country, Department, Employee, EmploymentPeriod, Role


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


@pytest.fixture
def two_employees(db):
    dept_a = Department.objects.create(name="Engineering")
    dept_b = Department.objects.create(name="Sales")
    role_a = Role.objects.create(name="Manager")
    role_b = Role.objects.create(name="Associate")
    country_a = Country.objects.create(name="India")
    country_b = Country.objects.create(name="USA")

    employee_a = Employee.objects.create(
        employee_code="E001",
        first_name="Alice",
        last_name="Anderson",
        email="alice@example.com",
        department=dept_a,
        role=role_a,
        country=country_a,
        hire_date="2020-01-01",
    )
    EmploymentPeriod.objects.create(employee=employee_a, effective_from="2020-01-01")

    employee_b = Employee.objects.create(
        employee_code="E002",
        first_name="Bob",
        last_name="Brown",
        email="bob@example.com",
        department=dept_b,
        role=role_b,
        country=country_b,
        hire_date="2020-01-01",
    )
    EmploymentPeriod.objects.create(employee=employee_b, effective_from="2020-01-01")

    return {"a": employee_a, "b": employee_b}
