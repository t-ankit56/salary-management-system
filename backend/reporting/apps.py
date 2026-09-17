"""App config for ``reporting`` (payroll and headcount reports, resolved as of a date)."""

from django.apps import AppConfig


class ReportingConfig(AppConfig):
    """Django app configuration for ``reporting``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "reporting"
