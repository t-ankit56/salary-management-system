from django.urls import path

from salary.views import SalaryChangeView, SalaryCorrectionView

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
]
