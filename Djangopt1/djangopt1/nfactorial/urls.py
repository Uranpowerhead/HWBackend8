from django.urls import path, include
from . import views

urlpatterns = [path('nfactorial', views.nfactorial, name='nfactorial'),
               path('<int:one>/add/<int:two>/', views.add_numbers, name='add_numbers'),
               path('transform/<str:text>/', views.upper, name='transform'),
               path('check/<str:text>/', views.palindrome, name='palindrome'),
               path('calc/<int:one>/<str:operand>/<int:two>', views.calculator, name='calculator'),]