from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'core'

urlpatterns = [
    path('signup', signup),
    path('api-token-auth', obtain_auth_token),
    path('image/categories', get_all_categories),
    path('image', post_single_image_async),
    path('image/bulk', post_bulk_images_async),
    path('images', get_all_images),
]
