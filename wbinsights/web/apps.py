import os

from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':  # Проверка на основной процесс
            from web import scheduler
            scheduler.start()
