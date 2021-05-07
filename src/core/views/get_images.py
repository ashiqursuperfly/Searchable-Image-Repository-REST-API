from ..utils import *
from rest_framework.decorators import api_view, parser_classes
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db.models import Value
from rest_framework.parsers import FormParser
from django.core.files.storage import FileSystemStorage
from django.db.models import QuerySet
from django.contrib.postgres.search import SearchQuery


def execute_full_text_search(data: FullTextSearchModel):
    query = data.generate_search_query()
    vector = SearchVector(Params.description, Params.categories + '__' + Params.name, Params.country)
    results = Image.objects.annotate(
        rank=SearchRank(
            query=query,
            vector=vector,
            normalization=Value(0).bitor(Value(1))
        )
    ).filter(rank__gte=0.006).order_by('-rank')

    return results


def execute_image_search(features: str, narrowed: QuerySet):
    query = SearchQuery(features, search_type='plain')
    vector = SearchVector('orb_descriptor')
    results = narrowed.annotate(
        rank=SearchRank(
            query=query,
            vector=vector,
            normalization=Value(0).bitor(Value(1))
        )
    ).filter(rank__gte=0.006).order_by('-rank')

    return results


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
        return error_response(ErrorMsg.invalid_content_type("multipart/form-data found" + request.content_type),
                              status.HTTP_422_UNPROCESSABLE_ENTITY)

    if Params.img not in request.FILES:
        return error_response(ErrorMsg.missing_fields(f'{Params.img}'), status.HTTP_422_UNPROCESSABLE_ENTITY)

    img_file = request.FILES[Params.img]
    serializer = FullTextSearchModelSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(msg=ErrorMsg.bad_request(str(serializer.errors)),
                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    data: FullTextSearchModel = serializer.save()
    if data.validate():
        results = execute_full_text_search(data)

        fs = FileSystemStorage()
        filename = fs.save(img_file.name, img_file)
        uploaded_file_url = fs.path(filename)

        features = generate_features_from_image(uploaded_file_url)

        results = execute_image_search(features, results)
        response[Params.content] = ImageSerializerWithAllDetails.serialize(data=results, is_list=True)
        return Response(response)

    else:
        return error_response(
            msg=ErrorMsg.bad_request('Please Provide at least one of the fields for the full text search model.'),
            code=status.HTTP_422_UNPROCESSABLE_ENTITY)
