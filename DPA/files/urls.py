from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path('listfiles/', views.get_filelist_from_drive, name='listfiles'),
    path('open/<str:file_id>/', views.open_file, name='open_file'),
    path('download/<str:file_id>/', views.download_file, name='download_file'),
    path('uploads/', views.upload_file, name='upload_file'),
    path('delete/<str:file_id>/', views.delete_file, name='delete_file'),
    path('images/', views.show_images, name='show_images'),
    path('documents/', views.show_documents, name='show_documents'),
    path('videos/', views.show_videos, name='show_videos'),
    path('other/', views.show_other, name='show_other'),


]