from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Note(models.Model):
    title = models.CharField(max_length=50, null=False)
    note = models.CharField(null=False)
    tags = models.CharField(max_length=20, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')

    class Meta:
        unique_together = ('title', 'note', 'tags')
        db_table = 'notes'
