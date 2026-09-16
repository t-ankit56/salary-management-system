import datetime
from decimal import Decimal

from employees.models import Employee
from salary.models import SalaryPeriod


def record_salary_change(
    *,
    employee: Employee,
    base: Decimal,
    effective_from: datetime.date,
    allowance: Decimal = 0,
    yearly_bonus: Decimal = 0,
    currency: str = "USD",
) -> SalaryPeriod:
    pass
