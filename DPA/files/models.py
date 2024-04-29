from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/temp_uploads')

# Create your models here.
