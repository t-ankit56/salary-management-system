"""App config for ``accounts`` (the custom user model and session auth endpoints)."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Django app configuration for ``accounts``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
