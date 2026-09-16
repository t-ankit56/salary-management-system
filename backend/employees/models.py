from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint, Value

from common.constraints import DateRangeFunc


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)


class Employee(models.Model):
    employee_code = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="employees")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="employees")

    hire_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmploymentPeriod(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employment_periods"
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(effective_to__isnull=True) | Q(effective_to__gt=F("effective_from")),
                name="employment_period_end_after_start",
            ),
            UniqueConstraint(
                fields=["employee"],
                condition=Q(effective_to__isnull=True),
                name="one_open_employment_period_per_employee",
            ),
            ExclusionConstraint(
                name="no_overlapping_employment_period",
                expressions=[
                    ("employee", RangeOperators.EQUAL),
                    (
                        DateRangeFunc("effective_from", "effective_to", Value("[)")),
                        RangeOperators.OVERLAPS,
                    ),
                ],
            ),
        ]
