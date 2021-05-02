from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg2.utils import swagger_auto_schema
from .tasks import add


@swagger_auto_schema(
    method='get'
)
@api_view(['GET'])
def index(request):
    task = add.apply_async((2, 3), countdown=5)
    return Response({'data': str(task)})

