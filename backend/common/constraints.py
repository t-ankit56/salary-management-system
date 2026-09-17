"""Shared exclusion-constraint building block for half-open period models."""

from django.contrib.postgres.fields import DateRangeField
from django.db.models import Func


class DateRangeFunc(Func):
    """Wraps a model's ``[effective_from, effective_to)`` pair as a Postgres ``daterange``.

    Used by both ``EmploymentPeriod`` and ``SalaryPeriod`` in a ``GiST`` exclusion
    constraint, so no employee can have two overlapping periods.
    """

    function = "daterange"
    output_field = DateRangeField()
