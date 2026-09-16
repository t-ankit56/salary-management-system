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
