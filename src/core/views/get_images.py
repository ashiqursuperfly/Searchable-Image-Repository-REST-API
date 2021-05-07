from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser
from ..utils import *
from ..tasks import image_search_task
from django.core.files.storage import FileSystemStorage
from django.http import QueryDict

@extend_schema(
    responses=OpenApiResponse.image_list_response,
    request=FullTextSearchModelSerializer()
)
@api_view(['POST'])
def full_text_search(request):
    response = get_response_model()
    serializer = FullTextSearchModelSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(msg=ErrorMsg.bad_request(str(serializer.errors)),
                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    data: FullTextSearchModel = serializer.save()
    if data.validate():
        results = execute_full_text_search(data)
        response[Params.content] = ImageSerializerWithAllDetails.serialize(data=results, is_list=True)
        return Response(response)
    else:
        return error_response(msg=ErrorMsg.bad_request('Please Provide at least one of the fields'),
                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@extend_schema(
    request=ImageSearchRequestSerializer(),
    responses=OpenApiResponse.single_image_task_response
)
@parser_classes([FormParser, ])
@api_view(['POST'])
def image_search(request):
    response = get_response_model()

    if not str(request.content_type).startswith("multipart/form-data"):
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type), status.HTTP_422_UNPROCESSABLE_ENTITY)

    if Params.img not in request.FILES:
        return error_response(ErrorMsg.missing_fields(f'{Params.img}'), status.HTTP_422_UNPROCESSABLE_ENTITY)

    fs = FileSystemStorage()
    img_file = request.FILES[Params.img]
    filename = fs.save(img_file.name, img_file)
    uploaded_file_url = fs.path(filename)

    img_data = request.data
    if isinstance(img_data, QueryDict):
        img_data._mutable = True
    img_data.pop(Params.img)

    t = image_search_task.delay(uploaded_file_url, img_data)

    response[Params.content] = str(t)
    response[Params.detail] = 'You request is being processed. You can check the status of your request using the /task-result/{task_id} endpoint'

    return Response(response)
