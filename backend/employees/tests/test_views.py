import json

import pytest
from django.test import Client
from rest_framework.test import APIClient

from employees.models import Country, Department, Employee, EmploymentPeriod, Role
from employees.services import deactivate_employee
from salary.models import SalaryPeriod


@pytest.mark.django_db
def test_department_list_excludes_inactive(user):
    Department.objects.create(name="Engineering", is_active=True)
    Department.objects.create(name="Retired", is_active=False)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/departments/")

    names = [d["name"] for d in response.data]
    assert "Engineering" in names
    assert "Retired" not in names


@pytest.mark.django_db
def test_role_list_excludes_inactive(user):
    Role.objects.create(name="Manager", is_active=True)
    Role.objects.create(name="Retired", is_active=False)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/roles/")

    names = [r["name"] for r in response.data]
    assert "Manager" in names
    assert "Retired" not in names


@pytest.mark.django_db
def test_country_list_excludes_inactive(user):
    Country.objects.create(name="India", is_active=True)
    Country.objects.create(name="Retired", is_active=False)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/countries/")

    names = [c["name"] for c in response.data]
    assert "India" in names
    assert "Retired" not in names


@pytest.mark.django_db
def test_country_has_no_create_route(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/countries/", {"name": "France"})

    assert response.status_code == 405


def test_delete_employee_returns_405(reference_data, user):
    employee = Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2024-01-01",
        **reference_data,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.delete(f"/api/employees/{employee.id}/")

    assert response.status_code == 405


def test_create_employee_via_api_opens_both_periods(reference_data, user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
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


def test_create_employee_via_real_session_and_cross_origin_csrf(reference_data, user):
    # force_authenticate skips Django's real CSRF enforcement; this uses a real session instead.
    client = Client(enforce_csrf_checks=True)

    login_response = client.post(
        "/api/auth/login/",
        data=json.dumps({"email": "hr@example.com", "password": "s3cret-pass"}),
        content_type="application/json",
    )
    assert login_response.status_code == 200

    csrf_token = client.cookies["csrftoken"].value

    response = client.post(
        "/api/employees/",
        data=json.dumps(
            {
                "employee_code": "E002",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "department": reference_data["department"].id,
                "role": reference_data["role"].id,
                "country": reference_data["country"].id,
                "hire_date": "2020-01-01",
                "base": "50000",
                "salary_effective_from": "2020-01-01",
            }
        ),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_ORIGIN="http://localhost:5173",
    )

    assert response.status_code == 201


def test_deactivate_endpoint_closes_open_period(reference_data, user):
    employee = Employee.objects.create(
        employee_code="E001",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2020-01-01",
        **reference_data,
    )
    EmploymentPeriod.objects.create(employee=employee, effective_from="2020-01-01")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/employees/{employee.id}/deactivate/",
        {"effective_date": "2021-01-01"},
        format="json",
    )

    assert response.status_code == 200
    assert EmploymentPeriod.objects.get(employee=employee).effective_to is not None


def test_deactivate_endpoint_already_inactive_returns_400(reference_data, user):
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

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/employees/{employee.id}/deactivate/",
        {"effective_date": "2021-06-01"},
        format="json",
    )

    assert response.status_code == 400


def test_reactivate_endpoint_opens_new_period(reference_data, user):
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

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/employees/{employee.id}/reactivate/",
        {"effective_date": "2021-06-01"},
        format="json",
    )

    assert response.status_code == 200
    assert EmploymentPeriod.objects.filter(employee=employee, effective_to=None).exists()


def test_employee_list_filters_by_department(two_employees, user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/?department={two_employees['a'].department_id}")

    codes = [e["employee_code"] for e in response.data["results"]]
    assert codes == ["E001"]


def test_employee_list_filters_by_role(two_employees, user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/?role={two_employees['a'].role_id}")

    codes = [e["employee_code"] for e in response.data["results"]]
    assert codes == ["E001"]


def test_employee_list_filters_by_country(two_employees, user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/?country={two_employees['a'].country_id}")

    codes = [e["employee_code"] for e in response.data["results"]]
    assert codes == ["E001"]


def test_employee_list_filters_by_status(two_employees, user):
    deactivate_employee(employee=two_employees["a"], effective_date="2020-06-01")

    client = APIClient()
    client.force_authenticate(user=user)
    active = client.get("/api/employees/?status=active")
    inactive = client.get("/api/employees/?status=inactive")

    active_codes = [e["employee_code"] for e in active.data["results"]]
    inactive_codes = [e["employee_code"] for e in inactive.data["results"]]

    assert active_codes == ["E002"]
    assert inactive_codes == ["E001"]


def test_employee_list_search_matches_name_and_code(two_employees, user):
    client = APIClient()
    client.force_authenticate(user=user)
    by_name = client.get("/api/employees/?search=Alice")
    by_code = client.get("/api/employees/?search=E002")

    assert [e["employee_code"] for e in by_name.data["results"]] == ["E001"]
    assert [e["employee_code"] for e in by_code.data["results"]] == ["E002"]


def test_employee_list_includes_reference_names_and_status(two_employees, user):
    deactivate_employee(employee=two_employees["a"], effective_date="2020-06-01")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/employees/")

    by_code = {e["employee_code"]: e for e in response.data["results"]}
    assert by_code["E001"]["department_name"] == "Engineering"
    assert by_code["E001"]["role_name"] == "Manager"
    assert by_code["E001"]["country_name"] == "India"
    assert by_code["E001"]["status"] == "inactive"
    assert by_code["E002"]["status"] == "active"


def test_employee_detail_includes_reference_names_and_status(two_employees, user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/{two_employees['b'].id}/")

    assert response.data["department_name"] == "Sales"
    assert response.data["role_name"] == "Associate"
    assert response.data["country_name"] == "USA"
    assert response.data["status"] == "active"


def test_employee_list_requires_authentication(reference_data):
    response = APIClient().get("/api/employees/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_department_list_requires_authentication():
    response = APIClient().get("/api/departments/")

    assert response.status_code == 403


def test_employee_list_page_size_honoured(reference_data, user):
    for i in range(30):
        Employee.objects.create(
            employee_code=f"E{i:03d}",
            first_name="Jane",
            last_name="Doe",
            email=f"jane{i}@example.com",
            hire_date="2020-01-01",
            **reference_data,
        )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/employees/")

    assert len(response.data["results"]) == 25
    assert response.data["count"] == 30
