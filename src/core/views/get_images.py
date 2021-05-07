from ..utils import *
from rest_framework.decorators import api_view, parser_classes
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db.models import Value
from rest_framework.parsers import FormParser


@extend_schema(
    responses=OpenApiResponse.image_list_response,
    request=FullTextSearchModelSerializer
)
@api_view(['POST'])
def full_text_search(request):
    response = get_response_model()
    serializer = FullTextSearchModelSerializer(data=request.data)

    if not serializer.is_valid():
        response[Params.content] = serializer.errors
        return Response(response)

    data: FullTextSearchModel = serializer.save()
    if data.validate():
        query = data.generate_search_query()
        vector = SearchVector(Params.description, Params.categories + '__' + Params.name, Params.country)
        results = Image.objects.annotate(
            rank=SearchRank(
                query=query,
                vector=vector,
                normalization=Value(0).bitor(Value(1))
            )
        ).filter(rank__gte=0.006).order_by('-rank')

        response[Params.content] = ImageSerializerWithAllDetails.serialize(data=results, is_list=True)
    else:
        response[Params.content] = 'Please Provide at least one of the fields'

    return Response(response)


@extend_schema(
    parameters=[
        OpenApiParams.authorization
    ],
    request=SingleImageRequestSerializer(),
    responses=OpenApiResponse.single_image_task_response
)
@parser_classes([FormParser, ])
@api_view(['POST'])
def image_search(request):
    response = get_response_model()

    if not str(request.content_type).startswith("multipart/form-data"):
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type), status.HTTP_422_UNPROCESSABLE_ENTITY)

    if Params.img not in request.FILES:
        return error_response(ErrorMsg.missing_fields(f'{Params.img} is mandatory for image search'), status.HTTP_422_UNPROCESSABLE_ENTITY)

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

        return Response(response)

    except ValueError as e:
        return error_response(ErrorMsg.unknown_error(str(e)), status.HTTP_422_UNPROCESSABLE_ENTITY)
