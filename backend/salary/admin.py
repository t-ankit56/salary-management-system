from django.contrib import admin

from salary.models import SalaryPeriod


@admin.register(SalaryPeriod)
class SalaryPeriodAdmin(admin.ModelAdmin):
    list_display = [
        "employee",
        "base",
        "allowance",
        "yearly_bonus",
        "currency",
        "effective_from",
        "effective_to",
    ]
    list_filter = ["effective_to", "currency"]
