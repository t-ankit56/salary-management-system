from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView

from employees.models import Country, Department, Employee, Role
from employees.serializers import (
    CountrySerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    RoleSerializer,
)


class DepartmentListCreateView(ListCreateAPIView):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer


class DepartmentDetailView(RetrieveUpdateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class RoleListCreateView(ListCreateAPIView):
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer


class RoleDetailView(RetrieveUpdateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class CountryListView(ListAPIView):
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer


class CountryDetailView(RetrieveUpdateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class EmployeeListCreateView(ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetailView(RetrieveUpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
