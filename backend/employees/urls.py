from django.urls import path

from employees.views import (
    CountryDetailView,
    CountryListView,
    DepartmentDetailView,
    DepartmentListCreateView,
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
]
