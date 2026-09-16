from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from common.resolution import resolve_as_of
from salary.models import SalaryPeriod
from salary.services import record_salary_change


def test_recording_change_closes_old_period_and_opens_new_one(employee):
    old_period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01"
    )

    new_period = record_salary_change(employee=employee, base="60000", effective_from="2021-01-01")

    old_period.refresh_from_db()
    new_period.refresh_from_db()
    assert old_period.effective_to == date(2021, 1, 1)
    assert new_period.effective_from == date(2021, 1, 1)
    assert new_period.effective_to is None
    assert new_period.base == Decimal(60000)


def test_failed_salary_change_leaves_neither_period_modified(employee):
    old_period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01"
    )

    with pytest.raises(IntegrityError):
        record_salary_change(employee=employee, base=None, effective_from="2021-01-01")

    old_period.refresh_from_db()
    assert old_period.effective_to is None
    assert SalaryPeriod.objects.filter(employee=employee).count() == 1


def test_backdating_before_open_period_start_rejected(employee):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-06-01")

    with pytest.raises(ValueError):
        record_salary_change(employee=employee, base="60000", effective_from="2020-01-01")


def test_forward_dated_change_does_not_alter_todays_resolved_salary(employee):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-01-01")

    record_salary_change(employee=employee, base="60000", effective_from="2099-01-01")

    today_period = resolve_as_of(
        SalaryPeriod.objects.filter(employee=employee), timezone.localdate()
    )
    assert today_period.base == Decimal(50000)
