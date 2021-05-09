from ..utils import *
from django_celery_results.models import TaskResult
from rest_framework.decorators import api_view
import json


@extend_schema(
    responses=TaskResultSerializer
)
@api_view(['GET'])
def get_task_result(request, task_id):

    data = TaskResult.objects.filter(task_id=task_id)[0]

    response = get_response_model()
    res = {'status': data.status, 'result': json.loads(data.result), 'date_created': data.date_created, 'date_done': data.date_done}
    response[Params.content] = res

    return Response(response)
