import asyncio
import os
from time import sleep

from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from aiogoogle import Aiogoogle
from django.views import View
from googleapiclient.http import MediaFileUpload

from .async_google_drive.helpers import user_creds, client_creds
import aiogoogle
from .forms import FileUploadForm


async def get_filelist_from_drive(request):
    folder_id = '1Q2U0yza0P1yH_l7R4VnIQHcsuyELbkM2'
    documents = {}
    videos = {}
    images = {}
    other = {}

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        # Use the aiogoogle client to list files
        res = await aiogoogle.as_user(drive_v3.files.list(q=f"'{folder_id}' in parents and trashed=false"),
                                      full_res=True)
        async for page in res:
            for file in page.get("files"):
                mime_type = file.get("mimeType")
                file_info = [file.get('name'), file.get('id')]
                match mime_type.split('/')[0]:
                    case 'application' | 'text':
                        documents[file.get('name')] = file.get('id')
                    case 'video':
                        videos[file.get('name')] = file.get('id')
                    case 'image':
                        images[file.get('name')] = file.get('id')
                    case _:  # Catch all other files
                        other[file.get('name')] = file.get('id')
    return render(request, 'files/async_show_files_list.html', {
        'documents': documents,
        'videos': videos,
        'images': images,
        'other': other
    })


async def open_file(request, file_id):
    path_to_temporary_file = await create_file_with_correct_name(file_id)
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_user(
        drive_v3.files.get(fileId=file_id, download_file=path_to_temporary_file, alt='media'), )

    return FileResponse(open(path_to_temporary_file, 'rb'))


async def download_file(request, file_id):
    path_to_temporary_file = await create_file_with_correct_name(file_id)
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_user(
        drive_v3.files.get(fileId=file_id, download_file=path_to_temporary_file, alt='media'), )

    response = FileResponse(open(path_to_temporary_file, 'rb'), as_attachment=True)

    return response


async def create_file_with_correct_name(file_id):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        res = await aiogoogle.as_user(drive_v3.files.get(fileId=file_id))
        path = f'media/uploads/temp_upload/{res['name']}'
        fd = os.open(path, os.O_CREAT, 0o666)
        os.close(fd)
        return path


def clean_temp_folder():
    folder_path = 'media/upload/temp_download'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.unlink(file_path)


def authorize(request):
    uri = aiogoogle.oauth2.authorization_url(
        client_creds={
            'client_id': '222206179817-7oevt5trglkssvufbv58f7kf1ko4qstr.apps.googleusercontent.com',
            'client_secret': '"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"',
            'scopes': [
                'https://www.googleapis.com/auth/drive.file',
                'email',
                'https://www.googleapis.com/auth/drive.install'
            ],
            'redirect_uri': 'http://localhost:5000/callback/aiogoogle'
        },
    )
    return redirect(uri)


def upload():
    pass
