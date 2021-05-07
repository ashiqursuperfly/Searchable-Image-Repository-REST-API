from rest_framework.decorators import api_view
from ..utils import *


@extend_schema(
    parameters=[OpenApiParams.authorization],
    responses=OpenApiResponse.single_image_task_response
)
@api_view(['DELETE'])
def get_my_images(request):
    response = get_response_model()
    user = get_user_from_token(request.headers)

    if user is None:
        return error_response(ErrorMsg.invalid_or_missing_token(), status.HTTP_401_UNAUTHORIZED)

    res = Image.objects.filter(owner_id=user.id)
    response[Params.content] = ImageSerializerWithAllDetails.serialize(res, is_list=True)
    return Response(response)


@extend_schema(
    parameters=[OpenApiParams.authorization],
    responses=OpenApiResponse.single_image_task_response
)
@api_view(['DELETE'])
def delete_my_image(request, image_id: int):
    response = get_response_model()
    user = get_user_from_token(request.headers)

    if user is None:
        return error_response(ErrorMsg.invalid_or_missing_token(), status.HTTP_401_UNAUTHORIZED)

    item = Image.objects.filter(id=image_id)
    if item:
        if item[0].owner.id is not user.id:
            return error_response('Unauthorized, content does not belong to this user.', status.HTTP_401_UNAUTHORIZED)

        response[Params.content] = ImageSerializerWithAllDetails.serialize(item[0])
        return Response(response)

    return error_response(ErrorMsg.does_not_exist(), status.HTTP_422_UNPROCESSABLE_ENTITY)



