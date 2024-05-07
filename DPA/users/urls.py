from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.RegisterView.as_view(template_name='users/register.html'), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('accounts/profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='reset_password'),
    path('password_reset/reset_password_sent/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(success_url = reverse_lazy('users:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
