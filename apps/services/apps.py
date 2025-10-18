from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.services.signals  # noqa

