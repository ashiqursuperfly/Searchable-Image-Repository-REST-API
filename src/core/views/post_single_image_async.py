from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser

from ..tasks import upload_single_image_task
from ..utils import *


@extend_schema(
    parameters=[
        OpenApiParams.authorization
    ],
    request=SingleImageRequestSerializer(),
    responses=OpenApiResponse.single_image_task_response
)
@parser_classes([FormParser, ])
@api_view(['POST'])
def post_single_image_async(request):
    response = get_response_model()
    user = get_user_from_token(request.headers)

    if user is None:
        return error_response(ErrorMsg.invalid_or_missing_token(), status.HTTP_401_UNAUTHORIZED)

    if not str(request.content_type).startswith("multipart/form-data"):
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type), status.HTTP_422_UNPROCESSABLE_ENTITY)

    if Params.img not in request.FILES or Params.description not in request.data:
        return error_response(ErrorMsg.missing_fields(f'{Params.img} and {Params.description} are mandatory'), status.HTTP_422_UNPROCESSABLE_ENTITY)

    try:
        img_file = request.FILES[Params.img]
        description = get_safe_value_from_dict(request.data, Params.description)
        country_code = get_safe_value_from_dict(request.data, Params.country)
        categories = get_safe_value_from_dict(request.data, Params.categories)

        fs = FileSystemStorage()
        filename = fs.save(img_file.name, img_file)
        uploaded_file_url = fs.path(filename)

        s3_key = Image.generate_s3_key(filename)

        t = upload_single_image_task.delay(s3_key, uploaded_file_url, user.id, description, country_code, categories)
        response[Params.content] = {str(t): s3_key}
        response[Params.detail] = 'You request is being processed. You can check the status of your request using the /task-result/{task_id} endpoint'

        return Response(response)

    except ValueError as e:
        return error_response(ErrorMsg.unknown_error(str(e)), status.HTTP_422_UNPROCESSABLE_ENTITY)
