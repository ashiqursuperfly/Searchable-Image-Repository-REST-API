from django_countries import countries
from rest_framework.decorators import api_view
from ..utils import *


@extend_schema(
    responses=OpenApiResponse.country_list_response
)
@api_view(['GET'])
def get_all_countries(request):
    response = get_response_model()
    data = list()
    for k, v in countries:
        data.append({k: v})

    response[Params.content] = data
    return Response(response)
