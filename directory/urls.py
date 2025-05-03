from django.urls import path
from . import views

urlpatterns = [
    path('', views.escort_list, name='escort_list'),  # Homepage: list escorts
    path('escort/<int:pk>/', views.escort_detail, name='escort_detail'),
    path('escort/create/', views.create_escort_profile, name='create_escort_profile'),
    path('escort/edit/', views.edit_escort_profile, name='edit_escort_profile'),
    path('escort/add/', views.escort_create, name='escort_create'),  # Extra creation method
]