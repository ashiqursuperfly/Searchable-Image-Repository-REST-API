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
    s3_key: str,
    filepath: str,
    owner_id: int,
    description: str,
    country_code: str = None,
    comma_separated_category_ids: str = None  # not a list just a comma separated string
):
    logger.info(upload_single_image_task.__name__)
    res = upload_s3(filepath, s3_key)

    if res:
        image_data = Image()
        image_data.img.name = s3_key
        image_data.owner = get_user_model().objects.get(id=owner_id)
        image_data.description = description

        if country_code:
            image_data.country = Country(code=country_code)
        image_data.save() # need to save first before setting many to many field

        if comma_separated_category_ids:
            categories = comma_separated_category_ids.split(',')
            categories = [str(c).strip() for c in categories]
            image_data.categories.set(categories)  # assigning a list of ids sets the many to many relation

        fs = FileSystemStorage()
        fs.delete(filepath)
        return ImageSerializer.serialize(data=image_data)
    else:
        return None
