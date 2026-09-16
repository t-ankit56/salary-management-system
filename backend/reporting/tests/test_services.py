from datetime import date
from decimal import Decimal

import pytest

from employees.models import Country, Department, Employee, EmploymentPeriod
from employees.services import create_employee, deactivate_employee
from reporting.services import (
    ReportDateTooEarly,
    average_bonus_by_department,
    average_salary_by_country,
    average_salary_by_department,
    headcount_by_country,
    headcount_by_department,
    total_payroll_cost,
)
from salary.services import record_salary_change


def test_total_payroll_cost_correct_aggregate(reference_data):
    dept_sales = Department.objects.create(name="Sales")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        allowance="1000",
        yearly_bonus="2000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E002",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=dept_sales,
        role=reference_data["role"],
        country=reference_data["country"],
        hire_date="2020-01-01",
        base="40000",
        salary_effective_from="2020-01-01",
    )

    result = total_payroll_cost(as_of=date(2020, 6, 1))

    assert result["total_payroll_cost"] == Decimal(93000)
    assert result["excluded_count"] == 0


def test_headcount_by_department_correct_aggregate(reference_data):
    dept_sales = Department.objects.create(name="Sales")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E002",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=dept_sales,
        role=reference_data["role"],
        country=reference_data["country"],
        hire_date="2020-01-01",
        base="40000",
        salary_effective_from="2020-01-01",
    )

    result = headcount_by_department(as_of=date(2020, 6, 1))

    assert result["headcount_by_department"] == {"Engineering": 1, "Sales": 1}
    assert result["excluded_count"] == 0


def test_as_of_in_the_past_returns_historical_figure(reference_data):
    employee = create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    record_salary_change(employee=employee, base="60000", effective_from="2022-01-01")

    result = total_payroll_cost(as_of=date(2021, 1, 1))

    assert result["total_payroll_cost"] == Decimal(50000)


def test_inactive_employee_excluded(reference_data):
    dept_sales = Department.objects.create(name="Sales")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    employee_b = create_employee(
        employee_code="E002",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=dept_sales,
        role=reference_data["role"],
        country=reference_data["country"],
        hire_date="2020-01-01",
        base="40000",
        salary_effective_from="2020-01-01",
    )
    deactivate_employee(employee=employee_b, effective_date="2021-06-01")

    payroll = total_payroll_cost(as_of=date(2021, 7, 1))
    headcount = headcount_by_department(as_of=date(2021, 7, 1))

    assert payroll["total_payroll_cost"] == Decimal(50000)
    assert headcount["headcount_by_department"] == {"Engineering": 1}


def test_too_early_date_rejected(reference_data):
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )

    with pytest.raises(ReportDateTooEarly):
        total_payroll_cost(as_of=date(2019, 1, 1))


def test_missing_salary_period_increments_excluded_count(reference_data):
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    no_salary_employee = Employee.objects.create(
        employee_code="E002",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        hire_date="2020-01-01",
        **reference_data,
    )
    EmploymentPeriod.objects.create(employee=no_salary_employee, effective_from="2020-01-01")

    result = total_payroll_cost(as_of=date(2021, 1, 1))

    assert result["total_payroll_cost"] == Decimal(50000)
    assert result["excluded_count"] == 1


def test_average_salary_by_department_correct_aggregate(reference_data):
    dept_sales = Department.objects.create(name="Sales")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        allowance="1000",
        yearly_bonus="2000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E002",
        first_name="Carol",
        last_name="C",
        email="carol@example.com",
        hire_date="2020-01-01",
        base="40000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E003",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=dept_sales,
        role=reference_data["role"],
        country=reference_data["country"],
        hire_date="2020-01-01",
        base="60000",
        salary_effective_from="2020-01-01",
    )

    result = average_salary_by_department(as_of=date(2020, 6, 1))

    assert result["average_salary_by_department"] == {
        "Engineering": Decimal(46500),
        "Sales": Decimal(60000),
    }
    assert result["excluded_count"] == 0


def test_average_salary_by_country_correct_aggregate(reference_data):
    country_usa = Country.objects.create(name="USA")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        allowance="1000",
        yearly_bonus="2000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E002",
        first_name="Carol",
        last_name="C",
        email="carol@example.com",
        hire_date="2020-01-01",
        base="40000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E003",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=reference_data["department"],
        role=reference_data["role"],
        country=country_usa,
        hire_date="2020-01-01",
        base="60000",
        salary_effective_from="2020-01-01",
    )

    result = average_salary_by_country(as_of=date(2020, 6, 1))

    assert result["average_salary_by_country"] == {
        "India": Decimal(46500),
        "USA": Decimal(60000),
    }
    assert result["excluded_count"] == 0


def test_average_bonus_by_department_correct_aggregate(reference_data):
    dept_sales = Department.objects.create(name="Sales")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        yearly_bonus="2000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E002",
        first_name="Carol",
        last_name="C",
        email="carol@example.com",
        hire_date="2020-01-01",
        base="40000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E003",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=dept_sales,
        role=reference_data["role"],
        country=reference_data["country"],
        hire_date="2020-01-01",
        base="60000",
        yearly_bonus="6000",
        salary_effective_from="2020-01-01",
    )

    result = average_bonus_by_department(as_of=date(2020, 6, 1))

    assert result["average_bonus_by_department"] == {
        "Engineering": Decimal(1000),
        "Sales": Decimal(6000),
    }
    assert result["excluded_count"] == 0


def test_headcount_by_country_correct_aggregate(reference_data):
    country_usa = Country.objects.create(name="USA")
    create_employee(
        employee_code="E001",
        first_name="Alice",
        last_name="A",
        email="alice@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )
    create_employee(
        employee_code="E002",
        first_name="Bob",
        last_name="B",
        email="bob@example.com",
        department=reference_data["department"],
        role=reference_data["role"],
        country=country_usa,
        hire_date="2020-01-01",
        base="60000",
        salary_effective_from="2020-01-01",
    )

    result = headcount_by_country(as_of=date(2020, 6, 1))

    assert result["headcount_by_country"] == {"India": 1, "USA": 1}
    assert result["excluded_count"] == 0
