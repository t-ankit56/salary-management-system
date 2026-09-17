"""Django admin registration for employees and their reference data."""

from django.contrib import admin

from employees.models import Country, Department, Employee, EmploymentPeriod, Role


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
        "role",
        "country",
    ]
    search_fields = ["employee_code", "first_name", "last_name", "email"]


@admin.register(EmploymentPeriod)
class EmploymentPeriodAdmin(admin.ModelAdmin):
    list_display = ["employee", "effective_from", "effective_to"]
    list_filter = ["effective_to"]
