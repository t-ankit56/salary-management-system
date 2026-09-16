import datetime

from django.db.models import Model, QuerySet


def resolve_as_of(queryset: QuerySet, as_of_date: datetime.date) -> Model | None:
    pass
