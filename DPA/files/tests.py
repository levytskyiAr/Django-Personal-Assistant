from models import UserFolderGoogleDrive
from django.contrib.auth.models import User

users = User.objects.all()
for user in users:
    print(user.id, user.email)


