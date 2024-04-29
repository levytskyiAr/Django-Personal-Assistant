from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # path('contacts/<str:user_id>/', views.get_user, name='author'),
    path('profile/', views.contact_list, name='profile'),
    path('profile/add_new_contact', views.create_contact, name='create_contact'),
]
