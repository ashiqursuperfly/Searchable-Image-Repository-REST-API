import json
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.parsers import FormParser
from ..utils import *
from django.core.files.storage import FileSystemStorage
from ..tasks import upload_single_image_task


# inline_serializer(
#         name='BulkImageUpload',
#         fields={
#             Params.images: serializers.ListField(child=serializers.FileField()),
#             Params.meta: serializers.ListField(child=ImageMetaSerializer())
#         }
#     )

@extend_schema(
    parameters=[
        OpenApiParams.authorization
    ],
    request=MultiImageRequestSerializer(),
    responses=OpenApiResponse.image_list_task_response
)
@parser_classes([FormParser, ])
@api_view(['POST'])
def post_bulk_images_async(request):
    response = get_response_model()
    user = get_user_from_token(request.headers)

    if user is None:
        return error_response(ErrorMsg.invalid_or_missing_token(), status.HTTP_401_UNAUTHORIZED)

    if not str(request.content_type).startswith("multipart/form-data"):
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type), status.HTTP_422_UNPROCESSABLE_ENTITY)

    if Params.images not in request.FILES or Params.meta not in request.data:
        return error_response(ErrorMsg.missing_fields(f'{Params.img} and {Params.meta} are mandatory'), status.HTTP_422_UNPROCESSABLE_ENTITY)

    meta = str(request.data[Params.meta])
    meta = "".join(meta.splitlines())
    meta = '[' + meta + ']'
    meta = json.loads(meta)

    if len(request.FILES.getlist(Params.images)) != len(meta) and len(meta) != 1:
        return error_response(ErrorMsg.bad_request('length of images and meta must be same'), status.HTTP_422_UNPROCESSABLE_ENTITY)

    try:
        img_files = request.FILES.getlist(Params.images)
        t_ids = []
        i = 0
        fs = FileSystemStorage()
        for img_file in img_files:

            file_meta = meta[0] if len(meta) == 1 else meta[i]

            description = get_safe_value_from_dict(file_meta, Params.description)
            if description is None:
                t_ids.append(ErrorMsg.missing_fields(Params.description, ext=f'Upload Aborted. file={img_file.name} index={i}'))
                i += 1
                continue

            filename = fs.save(img_file.name, img_file)
            uploaded_file_url = fs.path(filename)

            country = get_safe_value_from_dict(file_meta, Params.country)
            categories = get_safe_value_from_dict(file_meta, Params.categories)

            if categories:
                categories = str(categories)[1:-1]

            s3_key = Image.generate_s3_key(filename)
            t = upload_single_image_task.delay(s3_key, uploaded_file_url, user.id, description, country, categories)
            t_ids.append({str(t): f"https://{os.environ.get('AWS_CLOUDFRONT_DOMAIN')}/{s3_key}"})

            i += 1

        response[Params.content] = t_ids
        response[Params.detail] = 'You request is being processed. You can check the status of your request using the /task-result/{task_id} endpoint'

        return Response(response)

    except ValueError as e:
        return error_response(ErrorMsg.unknown_error(str(e)), status.HTTP_422_UNPROCESSABLE_ENTITY)
