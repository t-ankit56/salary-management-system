from django.contrib import admin

from employees.models import Country, Department, Employee, Role


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
