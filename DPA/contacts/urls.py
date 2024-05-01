from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('accounts/profile/', views.ContactListView.as_view(), name='profile'),
    path('accounts/profile/add_new_contact/', views.create_contact, name='create_contact'),
    path('accounts/profile/edit_contact/<int:contact_id>/', views.EditContactView.as_view(), name='edit_contact'),
    path('accounts/profile/delete_contact/<int:contact_id>/', views.delete_contact, name='delete_contact'),
]
