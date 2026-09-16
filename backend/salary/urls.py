from django.urls import path

from salary.views import SalaryChangeView

urlpatterns = [
    path(
        "employees/<int:employee_id>/salary-changes/",
        SalaryChangeView.as_view(),
        name="salary-change",
    ),
]
