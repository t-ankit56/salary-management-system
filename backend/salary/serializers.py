from rest_framework import serializers

from salary.models import SalaryCorrection, SalaryPeriod


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


class SalaryPeriodHistorySerializer(serializers.ModelSerializer):
    correction_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SalaryPeriod
        fields = [
            "id",
            "base",
            "allowance",
            "yearly_bonus",
            "currency",
            "effective_from",
            "effective_to",
            "correction_count",
        ]


class SalaryCorrectionInputSerializer(serializers.Serializer):
    salary_period = serializers.PrimaryKeyRelatedField(queryset=SalaryPeriod.objects.all())
    base = serializers.DecimalField(max_digits=12, decimal_places=2)
    allowance = serializers.DecimalField(max_digits=12, decimal_places=2)
    yearly_bonus = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField()


class SalaryCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryCorrection
        fields = [
            "id",
            "salary_period",
            "previous_base",
            "previous_allowance",
            "previous_yearly_bonus",
            "new_base",
            "new_allowance",
            "new_yearly_bonus",
            "reason",
            "created_by",
            "created_at",
        ]
