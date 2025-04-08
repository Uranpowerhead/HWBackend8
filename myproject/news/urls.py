from django.urls import path
from . import views
from .views import NewsUpdateView


urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    path('add/', views.news_create, name='news_create'),
    path('<int:news_id>/edit/', NewsUpdateView.as_view(), name='news_edit'),
]
