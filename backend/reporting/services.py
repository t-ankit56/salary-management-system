"""Payroll and headcount reports, each resolved as of a given date (default: today).

Reports never silently omit employees — a report that resolves salary
(``total_payroll_cost`` and the ``average_*`` reports) reports an ``excluded_count`` for
employed employees with no salary period covering ``as_of``, rather than a smaller number
presented as complete. Headcount reports carry no salary lookup, so their exclusion count
is always 0.
"""

import datetime
from decimal import Decimal

from django.db.models import Avg, Count, F, Q, QuerySet, Sum
from django.utils import timezone

from employees.models import Employee, EmploymentPeriod
from salary.models import SalaryPeriod


class ReportDateTooEarly(ValueError):
    """Raised when ``as_of`` predates the earliest salary data on record."""

    def __init__(self, earliest_date: datetime.date):
        self.earliest_date = earliest_date
        super().__init__(f"No salary data available before {earliest_date}")


def _validate_as_of(as_of: datetime.date) -> None:
    earliest = (
        SalaryPeriod.objects.order_by("effective_from")
        .values_list("effective_from", flat=True)
        .first()
    )
    if earliest is not None and as_of < earliest:
        raise ReportDateTooEarly(earliest)


def _employed_employees(as_of: datetime.date) -> QuerySet:
    active_ids = (
        EmploymentPeriod.objects.filter(effective_from__lte=as_of)
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gt=as_of))
        .values_list("employee_id", flat=True)
    )

    return Employee.objects.filter(id__in=active_ids, hire_date__lte=as_of)


def _employed_salary_periods(as_of: datetime.date) -> tuple[QuerySet, int]:
    employed = _employed_employees(as_of)
    resolved = SalaryPeriod.objects.filter(
        employee_id__in=employed.values_list("id", flat=True),
        effective_from__lte=as_of,
    ).filter(Q(effective_to__isnull=True) | Q(effective_to__gt=as_of))

    excluded_count = employed.count() - resolved.count()
    return resolved, excluded_count


def total_payroll_cost(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    periods, excluded_count = _employed_salary_periods(as_of)
    total = periods.aggregate(total=Sum(F("base") + F("allowance") + F("yearly_bonus")))["total"]

    return {
        "as_of": as_of,
        "total_payroll_cost": total or Decimal(0),
        "excluded_count": excluded_count,
    }


def headcount_by_department(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    counts = (
        _employed_employees(as_of)
        .values("department__name")
        .annotate(count=Count("id"))
        .order_by("department__name")
    )

    return {
        "as_of": as_of,
        "headcount_by_department": {row["department__name"]: row["count"] for row in counts},
        "excluded_count": 0,
    }


def average_salary_by_department(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    periods, excluded_count = _employed_salary_periods(as_of)
    rows = (
        periods.values("employee__department__name")
        .annotate(avg_salary=Avg(F("base") + F("allowance") + F("yearly_bonus")))
        .order_by("employee__department__name")
    )

    return {
        "as_of": as_of,
        "average_salary_by_department": {
            row["employee__department__name"]: row["avg_salary"] for row in rows
        },
        "excluded_count": excluded_count,
    }


def average_salary_by_country(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    periods, excluded_count = _employed_salary_periods(as_of)
    rows = (
        periods.values("employee__country__name")
        .annotate(avg_salary=Avg(F("base") + F("allowance") + F("yearly_bonus")))
        .order_by("employee__country__name")
    )

    return {
        "as_of": as_of,
        "average_salary_by_country": {
            row["employee__country__name"]: row["avg_salary"] for row in rows
        },
        "excluded_count": excluded_count,
    }


def average_bonus_by_department(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    periods, excluded_count = _employed_salary_periods(as_of)
    rows = (
        periods.values("employee__department__name")
        .annotate(avg_bonus=Avg("yearly_bonus"))
        .order_by("employee__department__name")
    )

    return {
        "as_of": as_of,
        "average_bonus_by_department": {
            row["employee__department__name"]: row["avg_bonus"] for row in rows
        },
        "excluded_count": excluded_count,
    }


def headcount_by_country(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    counts = (
        _employed_employees(as_of)
        .values("country__name")
        .annotate(count=Count("id"))
        .order_by("country__name")
    )

    return {
        "as_of": as_of,
        "headcount_by_country": {row["country__name"]: row["count"] for row in counts},
        "excluded_count": 0,
    }
