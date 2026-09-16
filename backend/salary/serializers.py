from rest_framework import serializers

from salary.models import SalaryPeriod


class SalaryChangeSerializer(serializers.Serializer):
    base = serializers.DecimalField(max_digits=12, decimal_places=2)
    allowance = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    yearly_bonus = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = serializers.CharField(max_length=3, default="USD")
    effective_from = serializers.DateField()


class SalaryPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryPeriod
        fields = [
            "id",
            "employee",
            "base",
            "allowance",
            "yearly_bonus",
            "currency",
            "effective_from",
            "effective_to",
        ]
