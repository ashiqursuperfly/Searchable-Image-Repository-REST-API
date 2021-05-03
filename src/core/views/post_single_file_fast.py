from django.http import QueryDict
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.parsers import MultiPartParser
from ..utils import *
from django.core.files.storage import FileSystemStorage
from ..tasks import upload_single_image_task


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
def post_single_image_fast(request):
    response = get_response_model()
    user = get_user_from_token(request.headers)

    if user is None:
        return error_response(ErrorMsg.invalid_or_missing_token(), status.HTTP_401_UNAUTHORIZED)

    if not str(request.content_type).startswith("multipart/form-data"):
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type), status.HTTP_400_BAD_REQUEST)

    try:
        img_file = request.FILES[Params.img]

        fs = FileSystemStorage()
        filename = fs.save(img_file.name, img_file)
        uploaded_file_url = fs.path(filename)

        t = upload_single_image_task.delay(filename, uploaded_file_url, user.id)
        # t = util_upload_single_image_task(filename, uploaded_file_url, user.id)
        response[Params.content] = str(t)

        return Response(response)

    except ValueError as e:
        return error_response(ErrorMsg.unknown_error(str(e)), status.HTTP_400_BAD_REQUEST)
