import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import DateField

from accounts.models import User
from employees.models import Employee
from salary.models import SalaryCorrection, SalaryPeriod


def record_salary_change(
    *,
    employee: Employee,
    base: Decimal,
    effective_from: datetime.date,
    allowance: Decimal = 0,
    yearly_bonus: Decimal = 0,
    currency: str = "USD",
) -> SalaryPeriod:
    effective_from = DateField().to_python(effective_from)
    open_period = SalaryPeriod.objects.get(employee=employee, effective_to__isnull=True)

    if effective_from <= open_period.effective_from:
        raise ValueError("Cannot backdate a change before the current period's start")

    with transaction.atomic():
        open_period.effective_to = effective_from
        open_period.save()

        new_period = SalaryPeriod.objects.create(
            employee=employee,
            base=base,
            allowance=allowance,
            yearly_bonus=yearly_bonus,
            currency=currency,
            effective_from=effective_from,
        )

    return new_period


def correct_salary_period(
    *,
    salary_period: SalaryPeriod,
    base: Decimal,
    allowance: Decimal,
    yearly_bonus: Decimal,
    reason: str,
    created_by: User,
) -> SalaryCorrection:
    pass
