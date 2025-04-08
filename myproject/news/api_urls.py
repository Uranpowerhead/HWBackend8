from django.urls import path
from .views import news_create_api

urlpatterns = [
    path('news/', news_create_api, name='news_create_api'),
]
