from ..utils import *
from django_celery_results.models import TaskResult
from rest_framework.decorators import api_view


@extend_schema(
    responses=TaskResultSerializer
)
@api_view(['GET'])
def get_task_result(request, task_id):

    data = TaskResult.objects.filter(task_id=task_id)
    response = get_response_model()
    response[Params.content] = TaskResultSerializer.serialize(data=data, is_list=True)

    return Response(response)
