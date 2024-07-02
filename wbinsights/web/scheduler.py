import asyncio
import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from services.async_rating import calculate_rating_for_all_experts
from wbinsights import settings

logger = logging.getLogger(__name__)


def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps prevent the database from filling up with old historical records.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def await_rating_calc():
    asyncio.run(calculate_rating_for_all_experts())

def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        await_rating_calc,
        trigger=CronTrigger(hour='0', minute='0'),
        id="calculate_rating",  # The same `id` defined in `apscheduler.jobstores`
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'my_scheduled_job'.")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=IntervalTrigger(seconds=3600),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )

    logger.info("Added job 'delete_old_job_executions'.")

    scheduler.start()
    logger.info("Scheduler started!")

    return scheduler
