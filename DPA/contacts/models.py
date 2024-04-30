from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=16)
    birthday = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_user')

    class Meta:
        unique_together = ('first_name', 'last_name', 'user')
        db_table = 'contacts'
