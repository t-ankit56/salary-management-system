import pytest
from rest_framework.test import APIClient

from employees.models import Country, Department, Role


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
