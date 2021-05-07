from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'core'

urlpatterns = [
    path('country', get_all_countries),
    path('signup', signup),
    path('api-token-auth', obtain_auth_token),
    path('images/categories', get_all_categories),
    path('images', post_single_image_async),
    path('images/bulk', post_bulk_images_async),
    path('images/mine', get_my_images),
    path('images/mine', delete_my_image),
    path('images/full-text-search', full_text_search),
    path('images/image-search', image_search),
    path('task-result/<str:task_id>', get_task_result)
]
