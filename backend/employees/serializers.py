from rest_framework import serializers

from employees.models import Country, Department, Employee, Role
from employees.services import create_employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "is_active"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "is_active"]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "is_active"]


class EmployeeSerializer(serializers.ModelSerializer):
    base = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)
    allowance = serializers.DecimalField(
        max_digits=12, decimal_places=2, write_only=True, default=0
    )
    yearly_bonus = serializers.DecimalField(
        max_digits=12, decimal_places=2, write_only=True, default=0
    )
    currency = serializers.CharField(max_length=3, write_only=True, default="USD")
    salary_effective_from = serializers.DateField(write_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "department",
            "role",
            "country",
            "hire_date",
            "created_at",
            "updated_at",
            "base",
            "allowance",
            "yearly_bonus",
            "currency",
            "salary_effective_from",
        ]

    def create(self, validated_data):
        return create_employee(**validated_data)


class StatusChangeSerializer(serializers.Serializer):
    effective_date = serializers.DateField()
