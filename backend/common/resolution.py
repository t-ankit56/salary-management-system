import datetime

from django.db.models import Model, Q, QuerySet


def resolve_as_of(queryset: QuerySet, as_of_date: datetime.date) -> Model | None:
    return queryset.filter(
        Q(effective_from__lte=as_of_date),
        Q(effective_to__isnull=True) | Q(effective_to__gt=as_of_date),
    ).first()
