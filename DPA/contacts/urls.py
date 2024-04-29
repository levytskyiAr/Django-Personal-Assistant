from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # path('contacts/<str:user_id>/', views.get_user, name='author'),
    path('contacts/', views.contact_list, name='contacts'),
]
