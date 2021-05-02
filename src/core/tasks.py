from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def add(x, y):
    return x + y


@task(name="test_task")
def test_task(self, data):
    logger.info("executing test task")