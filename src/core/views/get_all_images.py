from rest_framework.decorators import api_view
from ..utils import *


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


