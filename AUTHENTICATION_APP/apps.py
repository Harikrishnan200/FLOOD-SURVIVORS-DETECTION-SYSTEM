from django.apps import AppConfig


class AuthenticationAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AUTHENTICATION_APP'


    def ready(self):
        import AUTHENTICATION_APP.signals 
