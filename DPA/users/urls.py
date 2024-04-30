from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.RegisterView.as_view(template_name='users/register.html'), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
]
