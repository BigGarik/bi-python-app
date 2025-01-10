import logging
import os

from django.apps import AppConfig

logger = logging.getLogger("django-info")


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        logger.info('AppConfig ready called')
        if os.environ.get('RUN_MAIN') == 'true':
            logger.info('Starting scheduler...')
            from web.scheduler import start
            start()
