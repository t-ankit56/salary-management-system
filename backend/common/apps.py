"""App config for ``common`` (shared, cross-app database and resolution logic)."""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Django app configuration for ``common``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "common"
