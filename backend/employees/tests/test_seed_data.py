from django.core.management import call_command
from django.utils import timezone

from employees.management.commands.seed_data import DEMO_EMPLOYEE_COUNT
from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from reporting.services import (
    average_bonus_by_department,
    average_salary_by_country,
    average_salary_by_department,
    total_payroll_cost,
)
from salary.models import SalaryCorrection, SalaryPeriod


def test_seed_data_satisfies_all_constraints(db):
    call_command("seed_data", count=30)

    assert Department.objects.count() > 0
    assert Role.objects.count() > 0
    assert Country.objects.count() > 0
    assert Employee.objects.count() == 30 + DEMO_EMPLOYEE_COUNT
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


def test_seed_data_creates_deterministic_demo_cases(db):
    call_command("seed_data", count=30)

    full_history = Employee.objects.get(employee_code="DEMO001")
    assert full_history.salary_periods.count() > 4

    future_raise = Employee.objects.get(employee_code="DEMO002")
    open_period = SalaryPeriod.objects.get(employee=future_raise, effective_to__isnull=True)
    assert open_period.effective_from > timezone.localdate()

    corrected = Employee.objects.get(employee_code="DEMO003")
    assert SalaryCorrection.objects.filter(salary_period__employee=corrected).exists()

    deactivated = Employee.objects.get(employee_code="DEMO004")
    assert not EmploymentPeriod.objects.filter(
        employee=deactivated, effective_to__isnull=True
    ).exists()
