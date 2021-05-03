from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

urlpatterns = [
    path('signup', signup),
    path('api-token-auth', obtain_auth_token),
    path('image', post_single_image),
    path('images', get_all_images),
    path('image/fast', post_single_image_fast)
]
