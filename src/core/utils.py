from .documentation import *
from rest_framework.authtoken.models import Token
from django.utils.timezone import get_current_timezone
from datetime import datetime
from skimage.transform import resize
from botocore.exceptions import ClientError
import boto3
import os
import cv2


def generate_features_from_image(img_path: str):
    img_cv = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_cv = resize(img_cv, (500, int((img_cv.shape[1] * 500) / img_cv.shape[0])), order=0, anti_aliasing=True, preserve_range=True).astype('uint8')

    orb = cv2.ORB_create()
    kp, desc = orb.detectAndCompute(img_cv, None)

    return desc.dumps() if desc is not None else ""


def get_safe_value_from_dict(data, key):
    if key in data:
        return data[key]
    else:
        return None


def util_upload_single_image_task(filename: str, filepath: str, owner_id: int):
    s3_key = Image.S3_DIR + '/' + filename
    res = upload_s3(filepath, s3_key)

    if res:
        image_data = Image()
        image_data.img.name = s3_key
        image_data.owner = get_user_model().objects.get(id=owner_id)
        image_data.save()

        return image_data
    else:
        return "FAILED"


def upload_s3(local_file_path, s3_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")

    try:
        s3.upload_file(local_file_path, bucket_name, s3_key)
    except ClientError as e:
        print(f"failed uploading to s3 {e}")
        return False
    return True


def get_user_from_token(headers):
    try:
        split = str(headers[Params.auth]).split(' ')
        bearer, token = split[0], split[1]  # String is in format `Bearer <authtoken>`
        if str(bearer).strip() != "Bearer":
            return None
        user = Token.objects.get(key=token.strip()).user
        return user
    except (KeyError, Token.DoesNotExist) as e:
        return None


def get_datetime(date_str, dformat='%Y-%m-%d'):
    tz = get_current_timezone()
    dt = tz.localize(datetime.strptime(date_str, dformat))

    return dt


def get_date(date_str, dformat='%Y-%m-%d'):
    return datetime.strptime(date_str, dformat).date()


def str2bool(v):
    return v.lower() in ("true", "1")
