import pytest
from django.db import IntegrityError

from salary.models import SalaryPeriod


def test_overlapping_salary_periods_rejected(employee):
    SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01", effective_to="2021-01-01"
    )

    with pytest.raises(IntegrityError):
        SalaryPeriod.objects.create(
            employee=employee,
            base="55000",
            effective_from="2020-06-01",
            effective_to="2021-06-01",
        )


def test_second_open_salary_period_rejected(employee):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-01-01")

    with pytest.raises(IntegrityError):
        SalaryPeriod.objects.create(employee=employee, base="55000", effective_from="2021-01-01")


def test_salary_period_effective_to_before_effective_from_rejected(employee):
    with pytest.raises(IntegrityError):
        SalaryPeriod.objects.create(
            employee=employee,
            base="50000",
            effective_from="2020-06-01",
            effective_to="2020-01-01",
        )


def test_adjacent_salary_periods_sharing_boundary_accepted(employee):
    SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01", effective_to="2021-01-01"
    )

    SalaryPeriod.objects.create(employee=employee, base="55000", effective_from="2021-01-01")


def test_different_employees_overlapping_salary_periods_accepted(employee, other_employee):
    SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01", effective_to="2021-01-01"
    )
    SalaryPeriod.objects.create(
        employee=other_employee,
        base="60000",
        effective_from="2020-06-01",
        effective_to="2021-06-01",
    )
