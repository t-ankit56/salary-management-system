from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint, Value

from common.constraints import DateRangeFunc
from employees.models import Employee


class SalaryPeriod(models.Model):
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
