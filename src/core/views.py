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
    t = add.delay(2, 3)
    return Response({'data': str(t)})

