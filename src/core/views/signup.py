from rest_framework.decorators import api_view
from django.db.utils import IntegrityError
from ..utils import *


def revert(user_data):
    get_user_model().objects.filter(username=user_data[Params.username]).delete()


@extend_schema(
    request=UserSerializer,
    responses=OpenApiResponse.signup_response
)
@api_view(['POST'])
def signup(request):
    response = get_response_model()

    user_data = dict(request.data)

    if Params.username not in user_data:
        return error_response(ErrorMsg.missing_fields(Params.username), status.HTTP_422_UNPROCESSABLE_ENTITY)
    if Params.password not in user_data:
        return error_response(ErrorMsg.missing_fields(Params.password), status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_data = {Params.username: user_data[Params.username], Params.password: user_data[Params.password]}
    is_user_created = False

    try:
        user = get_user_model().objects.create_user(username=user_data[Params.username], password=user_data[Params.password])
        is_user_created = True
        token, created = Token.objects.get_or_create(user=user)

        user_data['token'] = token.key
        response[Params.content] = user_data
        return Response(response)

    except (ValueError, TypeError, KeyError) as e:
        if is_user_created:
            revert(user_data)
        return error_response(ErrorMsg.obj_creation_failure(str(e)), status.HTTP_422_UNPROCESSABLE_ENTITY)
    except IntegrityError as e:
        return error_response(ErrorMsg.already_exists('user', str(e)), status.HTTP_422_UNPROCESSABLE_ENTITY)

