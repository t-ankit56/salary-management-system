import pytest
from rest_framework.test import APIClient

from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from employees.services import deactivate_employee
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


def test_deactivate_endpoint_closes_open_period(reference_data):
    employee = Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        **reference_data,
    )
    EmploymentPeriod.objects.create(employee=employee, effective_from="2020-01-01")

    response = APIClient().post(
        f"/api/employees/{employee.id}/deactivate/",
        {"effective_date": "2021-01-01"},
        format="json",
    )

    assert response.status_code == 200
    assert EmploymentPeriod.objects.get(employee=employee).effective_to is not None


def test_deactivate_endpoint_already_inactive_returns_400(reference_data):
    employee = Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        **reference_data,
    )
    EmploymentPeriod.objects.create(
        employee=employee, effective_from="2020-01-01", effective_to="2021-01-01"
    )

    response = APIClient().post(
        f"/api/employees/{employee.id}/deactivate/",
        {"effective_date": "2021-06-01"},
        format="json",
    )

    assert response.status_code == 400


def test_reactivate_endpoint_opens_new_period(reference_data):
    employee = Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        **reference_data,
    )
    EmploymentPeriod.objects.create(
        employee=employee, effective_from="2020-01-01", effective_to="2021-01-01"
    )

    response = APIClient().post(
        f"/api/employees/{employee.id}/reactivate/",
        {"effective_date": "2021-06-01"},
        format="json",
    )

    assert response.status_code == 200
    assert EmploymentPeriod.objects.filter(employee=employee, effective_to=None).exists()


def test_employee_list_filters_by_department(two_employees):
    response = APIClient().get(f"/api/employees/?department={two_employees['a'].department_id}")

    codes = [e["employee_code"] for e in response.data["results"]]
    assert codes == ["E001"]


def test_employee_list_filters_by_role(two_employees):
    response = APIClient().get(f"/api/employees/?role={two_employees['a'].role_id}")

    codes = [e["employee_code"] for e in response.data["results"]]
    assert codes == ["E001"]


def test_employee_list_filters_by_country(two_employees):
    response = APIClient().get(f"/api/employees/?country={two_employees['a'].country_id}")

    codes = [e["employee_code"] for e in response.data["results"]]
    assert codes == ["E001"]


def test_employee_list_filters_by_status(two_employees):
    deactivate_employee(employee=two_employees["a"], effective_date="2020-06-01")

    active = APIClient().get("/api/employees/?status=active")
    inactive = APIClient().get("/api/employees/?status=inactive")

    active_codes = [e["employee_code"] for e in active.data["results"]]
    inactive_codes = [e["employee_code"] for e in inactive.data["results"]]

    assert active_codes == ["E002"]
    assert inactive_codes == ["E001"]


def test_employee_list_search_matches_name_and_code(two_employees):
    by_name = APIClient().get("/api/employees/?search=Alice")
    by_code = APIClient().get("/api/employees/?search=E002")

    assert [e["employee_code"] for e in by_name.data["results"]] == ["E001"]
    assert [e["employee_code"] for e in by_code.data["results"]] == ["E002"]


def test_employee_list_page_size_honoured(reference_data):
    for i in range(30):
        Employee.objects.create(
            employee_code=f"E{i:03d}",
            first_name="Jane",
            last_name="Doe",
            email=f"jane{i}@example.com",
            hire_date="2020-01-01",
            **reference_data,
        )

    response = APIClient().get("/api/employees/")

    assert len(response.data["results"]) == 25
    assert response.data["count"] == 30
