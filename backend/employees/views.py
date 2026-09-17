"""API views for employees and their reference data."""

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.filters import EmployeeFilter
from employees.models import Country, Department, Employee, Role
from employees.serializers import (
    CountrySerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    RoleSerializer,
    StatusChangeSerializer,
)
from employees.services import deactivate_employee, reactivate_employee


class EmployeePagination(PageNumberPagination):
    """Fixed page size for the employee list, matched by the frontend's own pagination."""

    page_size = 25


class DepartmentListCreateView(ListCreateAPIView):
    """List active departments, or create one."""

    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer


class DepartmentDetailView(RetrieveUpdateAPIView):
    """Retrieve or update a single department."""

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class RoleListCreateView(ListCreateAPIView):
    """List active roles, or create one."""

    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer


class RoleDetailView(RetrieveUpdateAPIView):
    """Retrieve or update a single role."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class CountryListView(ListAPIView):
    """List active countries."""

    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer


class CountryDetailView(RetrieveUpdateAPIView):
    """Retrieve or update a single country."""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class EmployeeListCreateView(ListCreateAPIView):
    """List employees (paginated, filterable, searchable), or create one with its opening salary."""

    queryset = Employee.objects.order_by("employee_code")
    serializer_class = EmployeeSerializer
    pagination_class = EmployeePagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = EmployeeFilter
    search_fields = ["first_name", "last_name", "employee_code"]


class EmployeeDetailView(RetrieveUpdateAPIView):
    """Retrieve or update (demographics only — never salary) a single employee."""

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDeactivateView(APIView):
    """Closes an employee's open employment period as of a given date."""

    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        serializer = StatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            deactivate_employee(employee=employee, **serializer.validated_data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class EmployeeReactivateView(APIView):
    """Opens a new employment period for an employee as of a given date."""

    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        serializer = StatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reactivate_employee(employee=employee, **serializer.validated_data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
