from decimal import Decimal

import pytest
from django.db import IntegrityError

from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from employees.services import create_employee
from salary.models import SalaryPeriod


@pytest.fixture
def reference_data(db):
    return {
        "department": Department.objects.create(name="Engineering"),
        "role": Role.objects.create(name="Manager"),
        "country": Country.objects.create(name="India"),
    }


def test_create_employee_opens_employment_period(reference_data):
    employee = create_employee(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )

    period = EmploymentPeriod.objects.get(employee=employee)
    assert str(period.effective_from) == "2020-01-01"
    assert period.effective_to is None


def test_create_employee_opens_salary_period(reference_data):
    employee = create_employee(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )

    salary_period = SalaryPeriod.objects.get(employee=employee)
    assert salary_period.base == Decimal(50000)
    assert salary_period.effective_to is None


def test_failed_employee_creation_creates_none_of_the_three(reference_data):
    with pytest.raises(IntegrityError):
        create_employee(
            employee_code="E001",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            hire_date="2020-01-01",
            base=None,
            salary_effective_from="2020-01-01",
            **reference_data,
        )

    assert Employee.objects.count() == 0
    assert EmploymentPeriod.objects.count() == 0
    assert SalaryPeriod.objects.count() == 0
