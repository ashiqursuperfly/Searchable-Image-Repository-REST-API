from __future__ import absolute_import, unicode_literals

import pickle
import cv2
import os
from .serializers import *
from celery.decorators import task
from celery import shared_task
from celery.utils.log import get_task_logger
from .utils import upload_s3, generate_feature_dumps_from_image, generate_features_from_image, execute_full_text_search
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
        features = generate_feature_dumps_from_image(filepath)

        image_data = Image()
        image_data.img.name = s3_key
        image_data.owner = get_user_model().objects.get(id=owner_id)
        image_data.description = description
        image_data.orb_descriptor = features

        if country_code:
            image_data.country = Country(code=country_code)
        image_data.save()  # need to save first before setting many to many field

        if comma_separated_category_ids:
            categories = comma_separated_category_ids.split(',')
            categories = [str(c).strip() for c in categories]
            image_data.categories.set(categories)  # assigning a list of ids sets the many to many relation

        fs = FileSystemStorage()
        fs.delete(filepath)
        return ImageSerializer.serialize(data=image_data)
    else:
        return None


@task(name="image search task")
def image_search_task(
        query_image: str,
        full_text_search_model_serialized: str
):
    logger.info(image_search_task.__name__)

    serializer = FullTextSearchModelSerializer(data=full_text_search_model_serialized)

    queryset = None
    if serializer.is_valid():
        text_search_model: FullTextSearchModel = serializer.save()
        if text_search_model.validate():
            queryset = execute_full_text_search(text_search_model)

    if queryset is None:
        queryset = Image.objects.all()

    results = []

    desc_a = generate_features_from_image(query_image)
    for item in queryset:
        desc_b = pickle.loads(item.orb_descriptor)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(desc_a, desc_b)
        if len(matches) != 0:
            similar_regions = [i for i in matches if i.distance < 50]
            match_percentage = len(similar_regions) / len(matches)
            if match_percentage > 0.05:
                results.append({'img': f"https://{os.environ.get('AWS_CLOUDFRONT_DOMAIN')}/{str(item.img)}", 'match': match_percentage})

    fs = FileSystemStorage()
    fs.delete(query_image)
    results = sorted(results, key=lambda k: k['match'], reverse=True)
    return results
