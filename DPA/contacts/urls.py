from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('accounts/profile', views.ContactListView.as_view(), name='profile'),
    path('accounts/profile/add_new_contact/', views.create_contact, name='create_contact'),
]
