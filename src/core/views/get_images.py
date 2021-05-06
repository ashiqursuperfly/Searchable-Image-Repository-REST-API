from ..utils import *
from rest_framework.decorators import api_view
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db.models import Value


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
