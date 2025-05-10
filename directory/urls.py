from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.escort_list, name='escort_list'),
    path('escort/<int:pk>/', views.escort_detail, name='escort_detail'),
    path('escort/create/', views.escort_create, name='escort_create'),
    path('escort/edit/', views.edit_escort_profile, name='edit_escort_profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # ... other urls
]

