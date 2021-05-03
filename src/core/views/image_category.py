from rest_framework.decorators import api_view
from ..utils import *


@extend_schema(
    responses=OpenApiResponse.image_category_list_response
)
@api_view(['GET'])
def get_all_categories(request):
    data = ImageCategory.objects.all()
    response = get_response_model()
    response[Params.content] = ImageCategorySerializer.serialize(data=data, is_list=True)

    return Response(response)


