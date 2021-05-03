from .documentation import *

from rest_framework.authtoken.models import Token

from django.utils.timezone import get_current_timezone
from datetime import datetime


def get_user_from_token(headers):
    try:
        split = str(headers[Params.auth]).split(' ')
        bearer, token = split[0], split[1]  # String is in format `Bearer <authtoken>`
        print(bearer, token)
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

