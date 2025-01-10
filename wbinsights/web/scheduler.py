import asyncio
import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from web.models.models import KeyIndicator
from web.services.async_rating import calculate_rating_for_all_experts
from wbinsights import settings
from web.services.cbr_key_indicators import get_combined_financial_rates

logger = logging.getLogger("django-info")


def delete_old_job_executions(max_age=604_800):
    """Удаляет старые записи о выполнении задач из базы данных."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def await_rating_calc():
    asyncio.run(calculate_rating_for_all_experts())


def cbr_key_indicators():
    result = get_combined_financial_rates()
    KeyIndicator.objects.all().delete()
    KeyIndicator.objects.create(indicators=result)


def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        cbr_key_indicators,
        trigger=CronTrigger(minute="*"), # 1 каждую минуту
        # trigger=CronTrigger(hour=3, minute=0),  # Ежедневная задача в 3 часа ночи
        id="cbr_key_indicators",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        await_rating_calc,
        trigger=CronTrigger(minute="*"),  # 1 каждую минуту
        # trigger=CronTrigger(day=1, hour=0, minute=0),  # выполнить 1 числа каждого месяца в 0 часов 0 минут
        id="calculate_rating",  # The same `id` defined in `apscheduler.jobstores`
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        delete_old_job_executions,
        trigger=IntervalTrigger(seconds=3600),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started.")
