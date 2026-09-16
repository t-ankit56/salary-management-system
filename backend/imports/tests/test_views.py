from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from employees.models import Employee

CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _upload_file(build_workbook, rows):
    buffer = build_workbook(rows)
    return SimpleUploadedFile("roster.xlsx", buffer.read(), content_type=CONTENT_TYPE)


def test_roster_upload_endpoint_creates_employees(reference_data, build_workbook):
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
    ]

    response = APIClient().post(
        "/api/imports/roster/",
        {"file": _upload_file(build_workbook, rows)},
        format="multipart",
    )

    assert response.status_code == 201
    assert response.data["created"] == 1
    assert Employee.objects.filter(employee_code="E001").exists()


def test_roster_upload_endpoint_returns_row_errors(reference_data, build_workbook):
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
    ]

    response = APIClient().post(
        "/api/imports/roster/",
        {"file": _upload_file(build_workbook, rows)},
        format="multipart",
    )

    assert response.status_code == 400
    assert response.data["errors"][0]["row"] == 2
    assert Employee.objects.count() == 0


def test_roster_upload_endpoint_requires_file():
    response = APIClient().post("/api/imports/roster/", {}, format="multipart")

    assert response.status_code == 400
