from django.http import QueryDict
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.parsers import MultiPartParser
from django.db.utils import IntegrityError
from .utils import *


def revert(user_data):
    get_user_model().objects.filter(username=user_data[Params.username]).delete()
    

@extend_schema(
    request=UserSerializer,
    responses=OpenApiResponse.single_image_response
)
@api_view(['POST'])
def signup(request):
    response = get_response_model()

    user_data = dict(request.data)

    if Params.username not in user_data:
        return error_response(ErrorMsg.missing_fields(Params.username), status.HTTP_400_BAD_REQUEST)
    if Params.password not in user_data:
        return error_response(ErrorMsg.missing_fields(Params.password), status.HTTP_400_BAD_REQUEST)

    user_data = {Params.username: user_data[Params.username], Params.password: user_data[Params.password]}
    is_user_created = False

    try:
        user = get_user_model().objects.create_user(username=user_data[Params.username], password=user_data[Params.password])
        is_user_created = True
        token, created = Token.objects.get_or_create(user=user)

        user_data['token'] = token.key
        response[Params.content] = user_data
        return Response(response)

    except (ValueError, TypeError, KeyError) as e:
        if is_user_created:
            revert(user_data)
        return error_response(ErrorMsg.obj_creation_failure(str(e)), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        return error_response(ErrorMsg.already_exists('user', str(e)), status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses=OpenApiResponse.image_list_response
)
@api_view(['GET'])
def get_all_images(request):
    # todo: add pagination, add another request that fetches only the user's images (maybe done using the search api ?)
    data = Image.objects.all()
    response = get_response_model()
    response[Params.content] = ImageSerializer.serialize(data=data, is_list=True)

    return Response(response)


@extend_schema(
    parameters=[
        OpenApiParams.authorization
    ],
    request=inline_serializer(
        name="Single File Upload Request",
        fields={
            Params.img: serializers.FileField()
        }
    ),
    responses=OpenApiResponse.single_image_response
)
@parser_classes([MultiPartParser])
@api_view(['POST'])
def upload_single_image(request):
    response = get_response_model()
    user = get_user_from_token(request.headers)

    if user is None:
        return error_response(ErrorMsg.invalid_or_missing_token(), status.HTTP_401_UNAUTHORIZED)

    if not str(request.content_type).startswith("multipart/form-data"):
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type), status.HTTP_400_BAD_REQUEST)

    try:
        img_data = request.data
        if isinstance(img_data, QueryDict):
            img_data._mutable = True

        img_data[Params.date_modified] = datetime.now()
        img_data[Params.owner] = user.id
        serializer = ImageSerializer(data=img_data)

        if serializer.is_valid():
            serializer.save()
            response[Params.content] = serializer.data
            return Response(response)
        else:
            return error_response(ErrorMsg.deserialization_failure(str(serializer.errors)))

    except ValueError as e:
        return error_response(ErrorMsg.unknown_error(str(e)), status.HTTP_400_BAD_REQUEST)
