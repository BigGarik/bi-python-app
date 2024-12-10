from django.apps import AppConfig
from django.db.models.signals import post_migrate


def start_scheduler(sender, **kwargs):
    from web.scheduler import start
    start()


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        import web.models.users
        #post_migrate.connect(start_scheduler, sender=self)
        start_scheduler()


