"""App config for ``salary`` (salary history, changes and corrections)."""

from django.apps import AppConfig


class SalaryConfig(AppConfig):
    """Django app configuration for ``salary``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "salary"
