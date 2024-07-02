from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        import web.models.users
        from web.scheduler import start
        #Данный метод будет выполнятся также при миграции, так что если таблицы для apschedule еще не сделаны, метод нужно отключить
        start()


