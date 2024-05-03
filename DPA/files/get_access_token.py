import asyncio

import aiogoogle
from aiogoogle.auth.utils import create_secret
from aiogoogle.auth.creds import UserCreds, ClientCreds

CLIENT_ID = '222206179817-7oevt5trglkssvufbv58f7kf1ko4qstr.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:5000/callback/aiogoogle'
SCOPES = ['https://www.googleapis.com/auth/drive']
REFRESH_TOKEN = '1//09viPch5Rwxk8CgYIARAAGAkSNwF-L9IrfaNwxe5rxTbC_2_wr2Z0_-AAg8166YUHU0AYvhXN1W25qrrxp-cMVK2HZhiVG0nE2zM'

user_creds_ = UserCreds(
    access_token=None,
    refresh_token=REFRESH_TOKEN,
    expires_at=None,
    scopes=['https://www.googleapis.com/auth/drive'],
    token_uri='https://oauth2.googleapis.com/token'

)

client_creds_ = ClientCreds(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=SCOPES,
    redirect_uri='http://localhost:5000/callback/aiogoogle'
)


async def get_new_access_token(refresh_token):
    # Create a new aiogoogle client
    client = aiogoogle.Aiogoogle(client_creds=client_creds_)

    await client.oauth2.refresh(user_creds_)

    return user_creds_.access_token


# Example usage:

async def main():
    refresh_token = '1//09viPch5Rwxk8CgYIARAAGAkSNwF-L9IrfaNwxe5rxTbC_2_wr2Z0_-AAg8166YUHU0AYvhXN1W25qrrxp-cMVK2HZhiVG0nE2zM'  # Replace with the actual refresh token
    new_access_token = await get_new_access_token(refresh_token)
    if new_access_token:
        print(f'New access token: {new_access_token}')
    else:
        print('Failed to refresh access token.')


if __name__ == '__main__':
    asyncio.run(main())
