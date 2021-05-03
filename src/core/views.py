from django.http import QueryDict
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.parsers import MultiPartParser

from .utils import *


@extend_schema(
    responses=OpenApiResponse.image_list_response
)
@api_view(['GET'])
def get_all_images(request):
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
        presc_data = request.data
        if isinstance(presc_data, QueryDict):
            presc_data._mutable = True

        presc_data[Params.date_modified] = datetime.now()
        presc_data[Params.owner] = user.id
        serializer = ImageSerializer(data=presc_data)

        if serializer.is_valid():
            serializer.save()
            response[Params.content] = serializer.data
            return Response(response)
        else:
            return error_response(ErrorMsg.deserialization_failure(str(serializer.errors)))

    except ValueError as e:
        return error_response(ErrorMsg.unknown_error(str(e)), status.HTTP_400_BAD_REQUEST)
