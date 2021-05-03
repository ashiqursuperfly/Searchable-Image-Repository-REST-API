from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes


class ErrorMsg:

    @staticmethod
    def invalid_content_type(param, ext=""):
        return f'expected request content-type {param} ' + ext

    @staticmethod
    def deserialization_failure(ext=""):
        return 'deserialization failed ' + ext

    @staticmethod
    def unknown_error(ext=""):
        return 'unknown error ' + ext

    @staticmethod
    def invalid_or_missing_token(ext=""):
        return 'Token invalid/unavailable in header ' + ext

    @staticmethod
    def firebase_phone_auth_failed(ext=""):
        return 'phone_number verification failed in server ' + ext

    @staticmethod
    def obj_creation_failure(ext=""):
        return 'Could not create object(s) ' + ext

    @staticmethod
    def already_exists(param, ext=""):
        return f'object {param} already exists ' + ext

    @staticmethod
    def missing_fields(param, ext=""):
        return f'field(s) missing in request {param} ' + ext

    @staticmethod
    def does_not_exist(ext=""):
        return f'object(s) does not exist ' + ext


class Params:
    owner = 'owner'
    detail = 'detail'
    content = 'content'
    error = 'error'
    auth = 'auth'
    img = 'img'
    user = 'user'
    username = 'username'
    password = 'password'
    id = 'id'
    content_type = 'Content-Type'
    date_modified = 'date_modified'


def get_response_model(detail='success', content=None):
    return {Params.detail: detail, Params.content: content}


def error_response(msg=ErrorMsg.unknown_error(), code=status.HTTP_404_NOT_FOUND):
    response = get_response_model()
    response[Params.detail] = msg

    return Response(response, status=code)


class OpenApiParams:
    authorization = OpenApiParameter(name=Params.auth, location=OpenApiParameter.HEADER, type=OpenApiTypes.STR, description="Expected Format:- Bearer {authtoken}")


class OpenApiResponse:
    image_list_response = {
        200: inline_serializer(
            name="ImageListResponse",
            fields={
                "detail": serializers.CharField(),
                "content": ImageSerializer(many=True)
            }
        )
    }

    single_image_response = {
        200: inline_serializer(
            name="SingleImageResponse",
            fields={
                "detail": serializers.CharField(),
                "content": ImageSerializer()
            }
        )
    }

    signup_response = {
        200: inline_serializer(
            name="SignupResponse",
            fields={
                "detail": serializers.CharField(),
                "content": ImageSerializer(many=True)
            }
        )
    }
