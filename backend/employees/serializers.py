"""Serializers for employees and their reference data."""

from django.utils import timezone
from rest_framework import serializers

from common.resolution import resolve_as_of
from employees.models import Country, Department, Employee, Role
from employees.services import create_employee


class DepartmentSerializer(serializers.ModelSerializer):
    """Read/write serializer for ``Department``."""

    class Meta:
        model = Department
        fields = ["id", "name", "is_active"]


class RoleSerializer(serializers.ModelSerializer):
    """Read/write serializer for ``Role``."""

    class Meta:
        model = Role
        fields = ["id", "name", "is_active"]


class CountrySerializer(serializers.ModelSerializer):
    """Read/write serializer for ``Country``."""

    class Meta:
        model = Country
        fields = ["id", "name", "is_active"]


class EmployeeSerializer(serializers.ModelSerializer):
    """Employee read/write shape, plus the write-only opening-salary fields used on create."""

    base = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)
    allowance = serializers.DecimalField(
        max_digits=12, decimal_places=2, write_only=True, default=0
    )
    yearly_bonus = serializers.DecimalField(
        max_digits=12, decimal_places=2, write_only=True, default=0
    )
    currency = serializers.CharField(max_length=3, write_only=True, default="USD")
    salary_effective_from = serializers.DateField(write_only=True)

    department_name = serializers.CharField(source="department.name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "department",
            "department_name",
            "role",
            "role_name",
            "country",
            "country_name",
            "status",
            "hire_date",
            "created_at",
            "updated_at",
            "base",
            "allowance",
            "yearly_bonus",
            "currency",
            "salary_effective_from",
        ]

    def get_status(self, obj: Employee) -> str:
        current = resolve_as_of(obj.employment_periods.all(), timezone.localdate())
        return "active" if current is not None else "inactive"

    def create(self, validated_data):
        return create_employee(**validated_data)


class StatusChangeSerializer(serializers.Serializer):
    """Shared payload shape for both deactivate and reactivate requests."""

    effective_date = serializers.DateField()
