from django.core.management import call_command

from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from reporting.services import (
    average_bonus_by_department,
    average_salary_by_country,
    average_salary_by_department,
    total_payroll_cost,
)
from salary.models import SalaryPeriod


def test_seed_data_satisfies_all_constraints(db):
    call_command("seed_data", count=30)

    assert Department.objects.count() > 0
    assert Role.objects.count() > 0
    assert Country.objects.count() > 0
    assert Employee.objects.count() == 30
    assert SalaryPeriod.objects.count() > Employee.objects.count()

    active = EmploymentPeriod.objects.filter(effective_to__isnull=True).count()
    assert active > 0
    assert active < Employee.objects.count()


def test_seed_data_reports_run_with_zero_exclusions(db):
    call_command("seed_data", count=30)

    assert total_payroll_cost()["excluded_count"] == 0
    assert average_salary_by_department()["excluded_count"] == 0
    assert average_salary_by_country()["excluded_count"] == 0
    assert average_bonus_by_department()["excluded_count"] == 0
