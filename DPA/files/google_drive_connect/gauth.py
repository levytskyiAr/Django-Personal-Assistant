
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth_instance = GoogleAuth()
gauth_instance.LoadClientConfigFile()
gauth_instance.LocalWebserverAuth()

drive = GoogleDrive(gauth_instance)
