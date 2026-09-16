from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.models import Employee
from salary.serializers import SalaryChangeSerializer, SalaryPeriodSerializer
from salary.services import record_salary_change


class SalaryChangeView(APIView):
    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        serializer = SalaryChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_period = record_salary_change(employee=employee, **serializer.validated_data)
        except (ValueError, IntegrityError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(SalaryPeriodSerializer(new_period).data, status=status.HTTP_201_CREATED)
