from __future__ import absolute_import, unicode_literals
from .serializers import *
from celery.decorators import task
from celery import shared_task
from celery.utils.log import get_task_logger
from .utils import upload_s3
from django.core.files.storage import FileSystemStorage
from django_countries.fields import Country

logger = get_task_logger(__name__)


@shared_task
def add(x, y):
    return x + y


@task(name="single file upload task")
def upload_single_image_task(
    filename: str,
    filepath: str,
    owner_id: int,
    description: str,
    country_code: str = None,
    categories=None
):
    logger.info(upload_single_image_task.__name__)
    s3_key = Image.S3_DIR + '/' + filename
    res = upload_s3(filepath, s3_key)

    if res:
        image_data = Image()
        image_data.img.name = s3_key
        image_data.owner = get_user_model().objects.get(id=owner_id)
        image_data.description = description

        if country_code:
            image_data.country = Country(code=country_code)
        image_data.save() # need to save first before setting many to many field

        if categories:
            categories = str(categories).split(',')  # categories come as comma separated ids e.g: 1,2
            image_data.categories.set(categories)  # assigning a list of ids sets the many to many relation

        fs = FileSystemStorage()
        fs.delete(filepath)
        return ImageSerializer.serialize(data=image_data)
    else:
        return None
