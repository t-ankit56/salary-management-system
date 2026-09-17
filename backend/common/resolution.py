"""Point-in-time resolution over half-open period querysets (employment, salary, ...)."""

import datetime

from django.db.models import Model, Q, QuerySet


def resolve_as_of(queryset: QuerySet, as_of_date: datetime.date) -> Model | None:
    """Returns the period covering ``as_of_date``, or ``None`` if none does.

    Generic over any queryset of ``effective_from``/``effective_to`` period rows —
    reused for both ``EmploymentPeriod`` and ``SalaryPeriod``.
    """
    return queryset.filter(
        Q(effective_from__lte=as_of_date),
        Q(effective_to__isnull=True) | Q(effective_to__gt=as_of_date),
    ).first()
