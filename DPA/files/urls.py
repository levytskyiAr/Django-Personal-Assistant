from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path('listfiles/', views.get_filelist_from_drive, name='listfiles'),
    path('show_files/<str:file_id>', views.show_image, name='show_file')

]