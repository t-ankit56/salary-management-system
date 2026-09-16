import pytest

from common.resolution import resolve_as_of
from employees.models import Country, Department, Employee, EmploymentPeriod, Role


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


def test_date_inside_closed_period_resolves(employee):
    period = EmploymentPeriod.objects.create(
        employee=employee, effective_from="2020-01-01", effective_to="2021-01-01"
    )

    result = resolve_as_of(EmploymentPeriod.objects.filter(employee=employee), "2020-06-01")

    assert result == period


def test_date_inside_open_period_resolves(employee):
    period = EmploymentPeriod.objects.create(employee=employee, effective_from="2021-01-01")

    result = resolve_as_of(EmploymentPeriod.objects.filter(employee=employee), "2022-01-01")

    assert result == period


def test_boundary_date_resolves_to_later_period(employee):
    EmploymentPeriod.objects.create(
        employee=employee, effective_from="2020-01-01", effective_to="2021-01-01"
    )
    later_period = EmploymentPeriod.objects.create(employee=employee, effective_from="2021-01-01")

    result = resolve_as_of(EmploymentPeriod.objects.filter(employee=employee), "2021-01-01")

    assert result == later_period


def test_date_before_all_periods_returns_none(employee):
    EmploymentPeriod.objects.create(employee=employee, effective_from="2020-01-01")

    result = resolve_as_of(EmploymentPeriod.objects.filter(employee=employee), "2019-01-01")

    assert result is None


def test_future_dated_period_not_returned_for_today(employee):
    EmploymentPeriod.objects.create(
        employee=employee, effective_from="2020-01-01", effective_to="2021-01-01"
    )
    EmploymentPeriod.objects.create(employee=employee, effective_from="2030-01-01")

    result = resolve_as_of(EmploymentPeriod.objects.filter(employee=employee), "2025-06-01")

    assert result is None
