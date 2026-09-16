from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.models import Country, Department, Employee, Role
from employees.serializers import (
    CountrySerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    RoleSerializer,
    StatusChangeSerializer,
)
from employees.services import deactivate_employee, reactivate_employee


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


class EmployeeDeactivateView(APIView):
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
    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        serializer = StatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reactivate_employee(employee=employee, **serializer.validated_data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
