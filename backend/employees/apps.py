"""App config for ``employees`` (employee records, reference data, employment periods)."""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    """Django app configuration for ``employees``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"
