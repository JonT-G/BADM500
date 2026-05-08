from django.apps import AppConfig


class FederationConfig(AppConfig):
    """
    Configuration for the federation app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'federation'

    def ready(self):
        from . import signals  # noqa: F401  (register signal handlers)""
