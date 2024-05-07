import sys
import os

from aiogoogle.auth.creds import (
    UserCreds,
    ClientCreds,
)
from dotenv import load_dotenv

load_dotenv()
sys.path.append("../..")

email = os.getenv('EMAIL')

user_creds = UserCreds(
    access_token=os.getenv('ACCESS_TOKEN'),
    refresh_token=os.getenv('REFRESH_TOKEN'),
    expires_at=os.getenv('EXPIRES_AT') or None,
)

client_creds = ClientCreds(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRETS'),
    scopes=['https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.install', 'email']
)
