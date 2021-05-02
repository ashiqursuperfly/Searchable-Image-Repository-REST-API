from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

urlpatterns = [
    path('api-token-auth', obtain_auth_token),
    path('index', index)
]
