from django.db import models
from django.contrib.auth.models import User


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/temp_download')


# Create your models here.
class UserFolderGoogleDrive(models.Model):
    folder_drive_id = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
