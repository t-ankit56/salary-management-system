import django_filters
from django.db.models import Q
from django.utils import timezone

from employees.models import Employee, EmploymentPeriod


class EmployeeFilter(django_filters.FilterSet):
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
