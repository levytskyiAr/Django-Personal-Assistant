from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=13)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    birthday = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_user')

    class Meta:
        unique_together = ('first_name', 'last_name', 'phone', 'user')
        db_table = 'contacts'
