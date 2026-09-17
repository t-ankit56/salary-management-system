"""URL routes for salary changes, corrections, and history."""

from django.urls import path

from salary.views import (
    SalaryChangeView,
    SalaryCorrectionView,
    SalaryPeriodCorrectionsView,
    SalaryPeriodHistoryView,
)

urlpatterns = [
    path(
        "employees/<int:employee_id>/salary-changes/",
        SalaryChangeView.as_view(),
        name="salary-change",
    ),
    path(
        "employees/<int:employee_id>/salary-corrections/",
        SalaryCorrectionView.as_view(),
        name="salary-correction",
    ),
    path(
        "employees/<int:employee_id>/salary-periods/",
        SalaryPeriodHistoryView.as_view(),
        name="salary-period-history",
    ),
    path(
        "employees/<int:employee_id>/salary-periods/<int:period_id>/corrections/",
        SalaryPeriodCorrectionsView.as_view(),
        name="salary-period-corrections",
    ),
]
