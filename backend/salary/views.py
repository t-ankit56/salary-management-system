"""API views for salary changes, corrections, and history."""

from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.models import Employee
from salary.models import SalaryCorrection, SalaryPeriod
from salary.serializers import (
    SalaryChangeSerializer,
    SalaryCorrectionInputSerializer,
    SalaryCorrectionSerializer,
    SalaryPeriodHistorySerializer,
    SalaryPeriodSerializer,
)
from salary.services import correct_salary_period, record_salary_change


class SalaryChangeView(APIView):
    """Records a new salary period (a raise) effective from a given date."""

    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        serializer = SalaryChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_period = record_salary_change(employee=employee, **serializer.validated_data)
        except (ValueError, IntegrityError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(SalaryPeriodSerializer(new_period).data, status=status.HTTP_201_CREATED)


class SalaryCorrectionView(APIView):
    """Corrects an existing salary period's amounts in place, logging the change."""

    permission_classes = [IsAuthenticated]

    def post(self, request, employee_id):
        get_object_or_404(Employee, id=employee_id)
        serializer = SalaryCorrectionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            correction = correct_salary_period(created_by=request.user, **serializer.validated_data)
        except (ValueError, IntegrityError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(SalaryCorrectionSerializer(correction).data, status=status.HTTP_201_CREATED)


class SalaryPeriodHistoryView(ListAPIView):
    """Lists an employee's salary periods, newest first, with each period's correction count."""

    serializer_class = SalaryPeriodHistorySerializer

    def get_queryset(self):
        return (
            SalaryPeriod.objects.filter(employee_id=self.kwargs["employee_id"])
            .annotate(correction_count=Count("corrections"))
            .order_by("-effective_from")
        )


class SalaryPeriodCorrectionsView(ListAPIView):
    """Lists the corrections logged against a single salary period."""

    serializer_class = SalaryCorrectionSerializer

    def get_queryset(self):
        return SalaryCorrection.objects.filter(
            salary_period_id=self.kwargs["period_id"],
            salary_period__employee_id=self.kwargs["employee_id"],
        )
