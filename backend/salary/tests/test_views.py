from rest_framework.test import APIClient

from salary.models import SalaryPeriod


def test_salary_change_closes_old_and_opens_new_period(employee):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-01-01")

    response = APIClient().post(
        f"/api/employees/{employee.id}/salary-changes/",
        {"base": "60000", "effective_from": "2021-01-01"},
        format="json",
    )

    assert response.status_code == 201
    assert SalaryPeriod.objects.filter(employee=employee, effective_to=None, base="60000").exists()


def test_salary_change_backdating_returns_400(employee):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-06-01")

    response = APIClient().post(
        f"/api/employees/{employee.id}/salary-changes/",
        {"base": "60000", "effective_from": "2020-01-01"},
        format="json",
    )

    assert response.status_code == 400
