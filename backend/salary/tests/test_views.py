from rest_framework.test import APIClient

from salary.models import SalaryPeriod
from salary.services import correct_salary_period


def test_salary_change_requires_authentication(employee):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-01-01")

    response = APIClient().post(
        f"/api/employees/{employee.id}/salary-changes/",
        {"base": "60000", "effective_from": "2021-01-01"},
        format="json",
    )

    assert response.status_code == 403


def test_salary_change_closes_old_and_opens_new_period(employee, user):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-01-01")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/employees/{employee.id}/salary-changes/",
        {"base": "60000", "effective_from": "2021-01-01"},
        format="json",
    )

    assert response.status_code == 201
    assert SalaryPeriod.objects.filter(employee=employee, effective_to=None, base="60000").exists()


def test_salary_change_backdating_returns_400(employee, user):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-06-01")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/employees/{employee.id}/salary-changes/",
        {"base": "60000", "effective_from": "2020-01-01"},
        format="json",
    )

    assert response.status_code == 400


def test_salary_correction_updates_amounts_and_logs(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01"
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/employees/{employee.id}/salary-corrections/",
        {
            "salary_period": period.id,
            "base": "55000",
            "allowance": "0",
            "yearly_bonus": "0",
            "reason": "Backpay adjustment",
        },
        format="json",
    )

    assert response.status_code == 201
    period.refresh_from_db()
    assert period.base == 55000
    assert period.corrections.filter(reason="Backpay adjustment", created_by=user).exists()


def test_salary_correction_missing_reason_returns_400(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01"
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/employees/{employee.id}/salary-corrections/",
        {
            "salary_period": period.id,
            "base": "55000",
            "allowance": "0",
            "yearly_bonus": "0",
            "reason": "",
        },
        format="json",
    )

    assert response.status_code == 400


def test_salary_periods_returned_newest_first_with_correction_counts(employee, user):
    period1 = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01", effective_to="2021-01-01"
    )
    period2 = SalaryPeriod.objects.create(
        employee=employee, base="55000", effective_from="2021-01-01"
    )
    correct_salary_period(
        salary_period=period2,
        base="56000",
        allowance=0,
        yearly_bonus=0,
        reason="Adjustment",
        created_by=user,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/{employee.id}/salary-periods/")

    assert response.status_code == 200
    results = response.data
    assert results[0]["id"] == period2.id
    assert results[0]["correction_count"] == 1
    assert results[1]["id"] == period1.id
    assert results[1]["correction_count"] == 0


def test_salary_period_corrections_endpoint_returns_log(employee, user):
    period = SalaryPeriod.objects.create(
        employee=employee, base="50000", effective_from="2020-01-01"
    )
    correct_salary_period(
        salary_period=period,
        base="55000",
        allowance=0,
        yearly_bonus=0,
        reason="Backpay",
        created_by=user,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/{employee.id}/salary-periods/{period.id}/corrections/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["reason"] == "Backpay"


def test_salary_period_amounts_serialise_as_strings(employee, user):
    SalaryPeriod.objects.create(employee=employee, base="50000", effective_from="2020-01-01")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/employees/{employee.id}/salary-periods/")

    assert isinstance(response.data[0]["base"], str)
