from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app = "users"

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    ]
