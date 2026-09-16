import datetime
from decimal import Decimal

from employees.models import Country, Department, Employee, Role


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
    pass
