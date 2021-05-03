from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .serializers import *
from celery.decorators import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def add(x, y):
    return x + y


@task(name="upload_single_image_task")
def upload_single_image_task(data: ImageSerializer):
    logger.info(upload_single_image_task.__name__)
    data.save()
