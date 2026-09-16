import datetime
from decimal import Decimal

from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from common.resolution import resolve_as_of
from employees.models import Employee, EmploymentPeriod
from salary.models import SalaryPeriod


class ReportDateTooEarly(ValueError):
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


def total_payroll_cost(as_of: datetime.date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    _validate_as_of(as_of)

    total = Decimal(0)
    excluded_count = 0

    for employee in _employed_employees(as_of):
        period = resolve_as_of(SalaryPeriod.objects.filter(employee=employee), as_of)
        if period is None:
            excluded_count += 1
            continue
        total += period.base + period.allowance + period.yearly_bonus

    return {"as_of": as_of, "total_payroll_cost": total, "excluded_count": excluded_count}


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
