import pytest
from rest_framework.test import APIClient

from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from salary.models import SalaryPeriod


@pytest.mark.django_db
def test_department_list_excludes_inactive():
    Department.objects.create(name="Engineering", is_active=True)
    Department.objects.create(name="Retired", is_active=False)

    response = APIClient().get("/api/departments/")

    names = [d["name"] for d in response.data]
    assert "Engineering" in names
    assert "Retired" not in names


@pytest.mark.django_db
def test_role_list_excludes_inactive():
    Role.objects.create(name="Manager", is_active=True)
    Role.objects.create(name="Retired", is_active=False)

    response = APIClient().get("/api/roles/")

    names = [r["name"] for r in response.data]
    assert "Manager" in names
    assert "Retired" not in names


@pytest.mark.django_db
def test_country_list_excludes_inactive():
    Country.objects.create(name="India", is_active=True)
    Country.objects.create(name="Retired", is_active=False)

    response = APIClient().get("/api/countries/")

    names = [c["name"] for c in response.data]
    assert "India" in names
    assert "Retired" not in names


@pytest.mark.django_db
def test_country_has_no_create_route():
    response = APIClient().post("/api/countries/", {"name": "France"})

    assert response.status_code == 405


def test_delete_employee_returns_405(reference_data):
    employee = Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2024-01-01",
        **reference_data,
    )

    response = APIClient().delete(f"/api/employees/{employee.id}/")

    assert response.status_code == 405


def test_create_employee_via_api_opens_both_periods(reference_data):
    response = APIClient().post(
        "/api/employees/",
        {
            "employee_code": "E001",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "department": reference_data["department"].id,
            "role": reference_data["role"].id,
            "country": reference_data["country"].id,
            "hire_date": "2020-01-01",
            "base": "50000",
            "salary_effective_from": "2020-01-01",
        },
        format="json",
    )

    assert response.status_code == 201
    employee = Employee.objects.get(employee_code="E001")
    assert EmploymentPeriod.objects.filter(employee=employee).exists()
    assert SalaryPeriod.objects.filter(employee=employee).exists()
