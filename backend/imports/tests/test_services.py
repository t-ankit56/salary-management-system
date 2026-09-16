from decimal import Decimal

import pytest

from employees.models import Employee, EmploymentPeriod
from employees.services import create_employee
from imports.services import RosterUploadError, import_roster
from salary.models import SalaryPeriod


def test_validation_failures_return_row_numbers(reference_data, build_workbook):
    rows = [
        [
            "E001",
            "Jane",
            "Doe",
            "jane@example.com",
            "NoSuchDept",
            "India",
            "Manager",
            "2020-01-01",
            50000,
            0,
            0,
            "2020-01-01",
        ],
        [
            "E002",
            "Bob",
            "Smith",
            "bob@example.com",
            "Engineering",
            "India",
            "Manager",
            "2020-01-01",
            -1000,
            0,
            0,
            "2020-01-01",
        ],
    ]
    workbook = build_workbook(rows)

    with pytest.raises(RosterUploadError) as exc_info:
        import_roster(workbook)

    rows_with_errors = {error["row"] for error in exc_info.value.errors}
    assert 2 in rows_with_errors
    assert 3 in rows_with_errors


def test_bad_row_writes_nothing(reference_data, build_workbook):
    rows = [
        [
            "E001",
            "Jane",
            "Doe",
            "jane@example.com",
            "Engineering",
            "India",
            "Manager",
            "2020-01-01",
            50000,
            0,
            0,
            "2020-01-01",
        ],
        [
            "E002",
            "Bob",
            "Smith",
            "bob@example.com",
            "Engineering",
            "India",
            "Manager",
            "2020-01-01",
            -1000,
            0,
            0,
            "2020-01-01",
        ],
    ]
    workbook = build_workbook(rows)

    with pytest.raises(RosterUploadError):
        import_roster(workbook)

    assert Employee.objects.count() == 0


def test_valid_file_creates_employees_with_both_periods(reference_data, build_workbook):
    rows = [
        [
            "E001",
            "Jane",
            "Doe",
            "jane@example.com",
            "Engineering",
            "India",
            "Manager",
            "2020-01-01",
            50000,
            1000,
            2000,
            "2020-01-01",
        ],
    ]
    workbook = build_workbook(rows)

    result = import_roster(workbook)

    employee = Employee.objects.get(employee_code="E001")
    assert result["created"] == 1
    assert EmploymentPeriod.objects.filter(employee=employee).exists()
    salary_period = SalaryPeriod.objects.get(employee=employee)
    assert salary_period.base == Decimal(50000)


def test_existing_employee_code_updates_demographics_only(reference_data, build_workbook):
    employee = create_employee(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        base="50000",
        salary_effective_from="2020-01-01",
        **reference_data,
    )

    rows = [
        [
            "E001",
            "Janet",
            "Doe",
            "janet@example.com",
            "Engineering",
            "India",
            "Manager",
            "2020-01-01",
            99999,
            0,
            0,
            "2020-01-01",
        ],
    ]
    workbook = build_workbook(rows)

    result = import_roster(workbook)

    employee.refresh_from_db()
    assert result["updated"] == 1
    assert employee.first_name == "Janet"
    assert employee.email == "janet@example.com"
    salary_period = SalaryPeriod.objects.get(employee=employee)
    assert salary_period.base == Decimal(50000)


def test_file_over_row_cap_rejected(reference_data, build_workbook):
    rows = [
        [
            f"E{i:05d}",
            "Jane",
            "Doe",
            f"jane{i}@example.com",
            "Engineering",
            "India",
            "Manager",
            "2020-01-01",
            50000,
            0,
            0,
            "2020-01-01",
        ]
        for i in range(10001)
    ]
    workbook = build_workbook(rows)

    with pytest.raises(RosterUploadError):
        import_roster(workbook)
