from django.urls import path

from employees.views import (
    CountryDetailView,
    CountryListView,
    DepartmentDetailView,
    DepartmentListCreateView,
    EmployeeDeactivateView,
    EmployeeDetailView,
    EmployeeListCreateView,
    EmployeeReactivateView,
    RoleDetailView,
    RoleListCreateView,
)

urlpatterns = [
    path("departments/", DepartmentListCreateView.as_view(), name="department-list"),
    path("departments/<int:pk>/", DepartmentDetailView.as_view(), name="department-detail"),
    path("roles/", RoleListCreateView.as_view(), name="role-list"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path("countries/", CountryListView.as_view(), name="country-list"),
    path("countries/<int:pk>/", CountryDetailView.as_view(), name="country-detail"),
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list"),
    path("employees/<int:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),
    path(
        "employees/<int:employee_id>/deactivate/",
        EmployeeDeactivateView.as_view(),
        name="employee-deactivate",
    ),
    path(
        "employees/<int:employee_id>/reactivate/",
        EmployeeReactivateView.as_view(),
        name="employee-reactivate",
    ),
]
