import datetime
from decimal import Decimal

from django.db import transaction

from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from salary.models import SalaryPeriod


def create_employee(
    *,
    employee_code: str,
    first_name: str,
    last_name: str,
    email: str,
    department: Department,
    role: Role,
    country: Country,
    hire_date: datetime.date,
    base: Decimal,
    salary_effective_from: datetime.date,
    allowance: Decimal = 0,
    yearly_bonus: Decimal = 0,
    currency: str = "USD",
) -> Employee:
    with transaction.atomic():
        employee = Employee.objects.create(
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            role=role,
            country=country,
            hire_date=hire_date,
        )
        EmploymentPeriod.objects.create(employee=employee, effective_from=hire_date)
        SalaryPeriod.objects.create(
            employee=employee,
            base=base,
            allowance=allowance,
            yearly_bonus=yearly_bonus,
            currency=currency,
            effective_from=salary_effective_from,
        )
    return employee


def deactivate_employee(*, employee: Employee, effective_date: datetime.date) -> EmploymentPeriod:
    pass


def reactivate_employee(*, employee: Employee, effective_date: datetime.date) -> EmploymentPeriod:
    pass
