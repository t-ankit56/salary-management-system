"""Salary history: periods, and corrections applied to a period in place."""

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint, Value

from accounts.models import User
from common.constraints import DateRangeFunc
from employees.models import Employee


class SalaryPeriod(models.Model):
    """A half-open ``[effective_from, effective_to)`` span of salary.

    A raise (``record_salary_change``) closes the open period and opens a new one. A
    correction (``correct_salary_period``) amends a period's amounts in place instead,
    logged via ``SalaryCorrection`` — these are deliberately separate operations, not one
    "edit salary" action.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_periods")

    base = models.DecimalField(max_digits=12, decimal_places=2)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yearly_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")

    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(effective_to__isnull=True) | Q(effective_to__gt=F("effective_from")),
                name="salary_period_end_after_start",
            ),
            UniqueConstraint(
                fields=["employee"],
                condition=Q(effective_to__isnull=True),
                name="one_open_salary_period_per_employee",
            ),
            ExclusionConstraint(
                name="no_overlapping_salary_period",
                expressions=[
                    ("employee", RangeOperators.EQUAL),
                    (
                        DateRangeFunc("effective_from", "effective_to", Value("[)")),
                        RangeOperators.OVERLAPS,
                    ),
                ],
            ),
        ]


class SalaryCorrection(models.Model):
    """An audit log entry for one correction: previous and new amounts, reason, and author."""

    salary_period = models.ForeignKey(
        SalaryPeriod, on_delete=models.CASCADE, related_name="corrections"
    )

    previous_base = models.DecimalField(max_digits=12, decimal_places=2)
    previous_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    previous_yearly_bonus = models.DecimalField(max_digits=12, decimal_places=2)

    new_base = models.DecimalField(max_digits=12, decimal_places=2)
    new_allowance = models.DecimalField(max_digits=12, decimal_places=2)
    new_yearly_bonus = models.DecimalField(max_digits=12, decimal_places=2)

    reason = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="salary_corrections"
    )
    created_at = models.DateTimeField(auto_now_add=True)
