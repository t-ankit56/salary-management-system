from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from common.resolution import resolve_as_of
from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from employees.services import create_employee, deactivate_employee, reactivate_employee
from salary.models import SalaryPeriod


@pytest.fixture
def reference_data(db):
    return {
        "department": Department.objects.create(name="Engineering"),
        "role": Role.objects.create(name="Manager"),
        "country": Country.objects.create(name="India"),
    }


def _create_active_employee(reference_data):
    return create_employee(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )


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


def test_deactivate_closes_open_employment_period(reference_data):
    employee = _create_active_employee(reference_data)

    deactivate_employee(employee=employee, effective_date="2021-01-01")

    period = EmploymentPeriod.objects.get(employee=employee)
    assert period.effective_to == date(2021, 1, 1)


def test_reactivate_opens_new_employment_period(reference_data):
    employee = _create_active_employee(reference_data)
    deactivate_employee(employee=employee, effective_date="2021-01-01")

    reactivate_employee(employee=employee, effective_date="2021-06-01")

    assert EmploymentPeriod.objects.filter(
        employee=employee, effective_from=date(2021, 6, 1), effective_to=None
    ).exists()


def test_deactivating_already_inactive_employee_rejected(reference_data):
    employee = _create_active_employee(reference_data)
    deactivate_employee(employee=employee, effective_date="2021-01-01")

    with pytest.raises(ValueError):
        deactivate_employee(employee=employee, effective_date="2021-06-01")


def test_reactivating_already_active_employee_rejected(reference_data):
    employee = _create_active_employee(reference_data)

    with pytest.raises(ValueError):
        reactivate_employee(employee=employee, effective_date="2021-01-01")


def test_status_resolves_correctly_before_during_and_after_gap(reference_data):
    employee = _create_active_employee(reference_data)
    deactivate_employee(employee=employee, effective_date="2021-01-01")
    reactivate_employee(employee=employee, effective_date="2021-06-01")

    periods = EmploymentPeriod.objects.filter(employee=employee)
    before = resolve_as_of(periods, date(2020, 6, 1))
    during_gap = resolve_as_of(periods, date(2021, 3, 1))
    after = resolve_as_of(periods, date(2021, 7, 1))

    assert before is not None
    assert during_gap is None
    assert after is not None
