from django.urls import path
from . import views

urlpatterns = [
    path('', views.escort_list, name='escort_list'),
    path('escort/<int:pk>/', views.escort_detail, name='escort_detail'),
    path('escort/create/', views.escort_create, name='escort_create'),
    path('escort/edit/', views.edit_escort_profile, name='edit_escort_profile'),
    path('register/', views.register, name='register'),
    # ... other urls
]

