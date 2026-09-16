from io import BytesIO

import openpyxl
import pytest

from employees.models import Country, Department, Role

HEADER = [
    "employee_code",
    "first_name",
    "last_name",
    "email",
    "department",
    "country",
    "role",
    "hire_date",
    "base",
    "allowance",
    "yearly_bonus",
    "salary_effective_from",
]


@pytest.fixture
def reference_data(db):
    return {
        "department": Department.objects.create(name="Engineering"),
        "role": Role.objects.create(name="Manager"),
        "country": Country.objects.create(name="India"),
    }


@pytest.fixture
def build_workbook():
    def _build(rows, header=HEADER):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(header)
        for row in rows:
            sheet.append(row)

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return buffer

    return _build
