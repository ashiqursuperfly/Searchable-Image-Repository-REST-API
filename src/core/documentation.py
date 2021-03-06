from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes


class ErrorMsg:

    @staticmethod
    def invalid_content_type(param, ext=''):
        return f'expected request content-type {param} ' + ext

    @staticmethod
    def deserialization_failure(ext=''):
        return 'deserialization failed ' + ext

    @staticmethod
    def unknown_error(ext=''):
        return 'unknown error ' + ext

    @staticmethod
    def invalid_or_missing_token(ext=''):
        return 'Token invalid/unavailable in header ' + ext

    @staticmethod
    def firebase_phone_auth_failed(ext=''):
        return 'phone_number verification failed in server ' + ext

    @staticmethod
    def obj_creation_failure(ext=''):
        return 'Could not create object(s) ' + ext

    @staticmethod
    def already_exists(param, ext=''):
        return f'object {param} already exists ' + ext

    @staticmethod
    def missing_fields(param, ext=''):
        return f'field(s) missing in request {param} ' + ext

    @staticmethod
    def does_not_exist(ext=''):
        return f'object(s) does not exist ' + ext

    @staticmethod
    def bad_request(ext=''):
        return f'bad request ' + ext


class Params:
    id = 'id'
    user = 'user'
    username = 'username'
    password = 'password'
    email = 'email'

    owner = 'owner'
    description = 'description'
    country = 'country'
    category = 'category'
    categories = 'categories'

    fulltext_search_model = 'fulltext_search_model'

    meta = 'meta'
    name = 'name'

    content = 'content'
    auth = 'auth'
    img = 'img'
    images = 'images'
    date_modified = 'date_modified'

    detail = 'detail'
    error = 'error'


def get_response_model(detail='success', content=None):
    return {Params.detail: detail, Params.content: content}


def error_response(msg=ErrorMsg.unknown_error(), code=status.HTTP_400_BAD_REQUEST):
    response = get_response_model()
    response[Params.detail] = msg

    return Response(response, status=code)


class OpenApiParams:
    authorization = OpenApiParameter(name=Params.auth, location=OpenApiParameter.HEADER, type=OpenApiTypes.STR, description='Expected Format:- Bearer {authtoken}')
    # phrase = OpenApiParameter(name='phrase', location=OpenApiParameter.QUERY, type=OpenApiTypes.STR)
    # country_or_code = OpenApiParameter(name='country_or_code', location=OpenApiParameter.QUERY, type=OpenApiTypes.STR)
    # keywords = OpenApiParameter(name='keywords', location=OpenApiParameter.QUERY, type=OpenApiTypes.STR)


class OpenApiResponse:

    signup_response = {
        200: inline_serializer(
            name='SignupResponse',
            fields={
                'detail': serializers.CharField(),
                'content': UserSerializer()
            }
        )
    }

    country_list_response = {
        200: inline_serializer(
            name='CountryListResponse',
            fields={
                'detail': serializers.CharField(),
                'content': serializers.ListField(child=CountryFieldSerializer(country_dict=True))
            }
        )
    }

    image_category_list_response = {
        200: inline_serializer(
            name='ImageCategoryListResponse',
            fields={
                'detail': serializers.CharField(),
                'content': ImageCategorySerializer(many=True)
            }
        )
    }

    image_list_response = {
        200: inline_serializer(
            name='ImageListResponse',
            fields={
                'detail': serializers.CharField(),
                'content': ImageSerializerWithAllDetails(many=True)
            }
        )
    }

    single_image_response = {
        200: inline_serializer(
            name='SingleImageResponse',
            fields={
                'detail': serializers.CharField(),
                'content': ImageSerializerWithAllDetails()
            }
        )
    }

    single_image_task_response = {
        200: inline_serializer(
            name='SingleImageUploadTaskResponse',
            fields={
                'detail': serializers.CharField(),
                'content': serializers.CharField()
            }
        )
    }

    image_list_task_response = {
        200: inline_serializer(
            name='ImageListUploadTaskResponse',
            fields={
                'detail': serializers.CharField(),
                'content': serializers.ListField(child=serializers.CharField())
            }
        )
    }

