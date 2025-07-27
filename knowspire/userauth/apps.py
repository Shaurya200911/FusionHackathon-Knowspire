# userauth/apps.py
from django.apps import AppConfig


class UserauthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "userauth"

    def ready(self):
        # import signals so they get registered
        from . import signals  # noqa: F401

