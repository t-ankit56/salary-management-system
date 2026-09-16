from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from employees.services import create_employee


@pytest.mark.django_db
def test_report_endpoint_requires_authentication():
    response = APIClient().get("/api/reports/total_payroll_cost/")

    assert response.status_code == 403


def test_report_endpoint_returns_total_payroll_cost(reference_data):
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

    response = APIClient().get("/api/reports/total_payroll_cost/?as_of=2020-06-01")

    assert response.status_code == 200
    assert Decimal(response.data["total_payroll_cost"]) == Decimal(50000)


def test_report_endpoint_too_early_date_returns_400(reference_data):
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

    response = APIClient().get("/api/reports/total_payroll_cost/?as_of=2019-01-01")

    assert response.status_code == 400


def test_report_endpoint_unknown_name_returns_404():
    response = APIClient().get("/api/reports/not_a_real_report/")

    assert response.status_code == 404
