from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from common.resolution import resolve_as_of
from salary.models import SalaryPeriod
from salary.services import correct_salary_period, record_salary_change


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


def test_correction_updates_amounts_in_place(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee,
        base="50000",
        allowance="500",
        yearly_bonus="1000",
        effective_from="2020-01-01",
        effective_to="2021-01-01",
    )

    correct_salary_period(
        salary_period=period,
        base="55000",
        allowance="600",
        yearly_bonus="1100",
        reason="Backpay adjustment",
        created_by=user,
    )

    period.refresh_from_db()
    assert period.base == Decimal(55000)
    assert period.allowance == Decimal(600)
    assert period.yearly_bonus == Decimal(1100)


def test_correction_does_not_change_dates(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01", effective_to="2021-01-01"
    )

    correct_salary_period(
        salary_period=period,
        base="55000",
        allowance=0,
        yearly_bonus=0,
        reason="Backpay adjustment",
        created_by=user,
    )

    period.refresh_from_db()
    assert period.effective_from == date(2020, 1, 1)
    assert period.effective_to == date(2021, 1, 1)


def test_correction_writes_log_with_previous_and_new_values(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee,
        base="50000",
        allowance="500",
        yearly_bonus="1000",
        effective_from="2020-01-01",
    )

    correction = correct_salary_period(
        salary_period=period,
        base="55000",
        allowance="600",
        yearly_bonus="1100",
        reason="Backpay adjustment",
        created_by=user,
    )

    assert correction.previous_base == Decimal(50000)
    assert correction.previous_allowance == Decimal(500)
    assert correction.previous_yearly_bonus == Decimal(1000)
    assert correction.new_base == Decimal(55000)
    assert correction.new_allowance == Decimal(600)
    assert correction.new_yearly_bonus == Decimal(1100)
    assert correction.reason == "Backpay adjustment"
    assert correction.created_by == user


def test_correction_missing_reason_rejected(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01"
    )

    with pytest.raises(ValueError):
        correct_salary_period(
            salary_period=period,
            base="55000",
            allowance=0,
            yearly_bonus=0,
            reason="",
            created_by=user,
        )


def test_past_date_resolution_reflects_corrected_amounts(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01", effective_to="2021-01-01"
    )

    correct_salary_period(
        salary_period=period,
        base="55000",
        allowance=0,
        yearly_bonus=0,
        reason="Backpay adjustment",
        created_by=user,
    )

    resolved = resolve_as_of(SalaryPeriod.objects.filter(employee=employee), date(2020, 6, 1))
    assert resolved.base == Decimal(55000)
