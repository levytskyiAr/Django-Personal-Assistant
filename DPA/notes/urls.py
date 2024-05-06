from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('notes/', views.NoteListView.as_view(), name='notes'),
    path('notes/create_note/', views.create_note, name='create_note'),
    path('notes/edit_note/<int:note_id>/', views.EditNoteView.as_view(), name='edit_note'),
    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('search_note/', views.search_note, name='search_note'),
]