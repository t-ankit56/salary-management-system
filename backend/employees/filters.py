"""Filters for the employee list endpoint (department/role/country, plus a derived status)."""

import django_filters
from django.db.models import Q
from django.utils import timezone

from employees.models import Employee, EmploymentPeriod


class EmployeeFilter(django_filters.FilterSet):
    """Adds ``status=active|inactive`` on top of the plain model-field filters.

    Status isn't a stored field — it's resolved from ``EmploymentPeriod`` as of today.
    """

    status = django_filters.ChoiceFilter(
        choices=[("active", "Active"), ("inactive", "Inactive")],
        method="filter_status",
    )

    class Meta:
        model = Employee
        fields = ["department", "role", "country"]

    def filter_status(self, queryset, name, value):
        today = timezone.localdate()
        active_ids = EmploymentPeriod.objects.filter(effective_from__lte=today).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gt=today)
        )

        if value == "active":
            return queryset.filter(id__in=active_ids.values_list("employee_id", flat=True))
        return queryset.exclude(id__in=active_ids.values_list("employee_id", flat=True))
