from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('content/', views.ContactListView.as_view(), name='content'),
    path('content/add_new_contact/', views.create_contact, name='create_contact'),
    path('content/edit_contact/<int:contact_id>/', views.EditContactView.as_view(), name='edit_contact'),
    path('content/delete_contact/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('content/upcoming_birthdays/', views.upcoming_birthdays, name='upcoming_birthdays'),
]
