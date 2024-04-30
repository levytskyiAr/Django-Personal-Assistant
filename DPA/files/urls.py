from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path('listfiles/', views.get_filelist_from_drive, name='listfiles'),
    path('open/<str:file_id>/', views.open_file, name='open_file'),
    path('download/<str:file_id>/', views.download_file, name='download_file'),
    path('upload/', views.upload_file, name='upload_file'),
    path('authorize/', views.authorize, name='authorize')


]

