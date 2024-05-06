import os

import aiogoogle
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import FileResponse
from aiogoogle import Aiogoogle
from asgiref.sync import async_to_sync, sync_to_async
from django.core.cache import cache

from .async_google_drive.helpers import user_creds, client_creds
from .forms import UploadFileForm
from .models import UserFolderGoogleDrive

TEMP = f'media/uploads/temp'


def get_cache_data(request):
    data = async_to_sync(get_file_list_from_drive)(get_folder_id_by_user(request.user))
    cache.set(request.user.id, data, timeout=3600)
    return data


def get_folder_id_by_user(user: User) -> str:
    with transaction.atomic():
        write_to_db, created = UserFolderGoogleDrive.objects.get_or_create(user=user)
        if created:
            get_user = User.objects.get(id=user.id)
            folder_name_for_drive = f"id^{user.id}__username^{get_user.username}"
            folder_id = async_to_sync(create_folder_on_drive)(folder_name_for_drive)
            write_to_db.folder_drive_id = folder_id
            write_to_db.save()
            print(write_to_db.folder_drive_id)
        return write_to_db.folder_drive_id


def get_filelist_from_drive(request):
    data = cache.get(request.user.id)
    if not data:
        data = get_cache_data(request)
    return render(request, 'files/base_for_files.html',
                  {'documents': data['documents'],
                   'images': data['images'], 'videos': data['videos'],
                   'other': data['other'], 'user_id': request.user.id
                   })


async def get_file_list_from_drive(folder_id):
    documents = {}
    videos = {}
    images = {}
    other = {}

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        res = await aiogoogle.as_user(drive_v3.files.list(q=f"'{folder_id}' in parents and trashed=false"),
                                      full_res=True)

        async for page in res:
            for file in page.get("files"):
                mime_type = file.get("mimeType")
                match mime_type.split('/')[0]:
                    case 'application' | 'text':
                        documents[file.get('name')] = file.get('id')
                    case 'video':
                        videos[file.get('name')] = file.get('id')
                    case 'image':
                        images[file.get('name')] = file.get('id')
                    case _:  # Catch all other files
                        other[file.get('name')] = file.get('id')
    data = {
        'documents': documents,
        'videos': videos,
        'images': images,
        'other': other
    }
    return data


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
        path = os.path.join(TEMP, res['name'])
        fd = os.open(path, os.O_CREAT, 0o666)
        os.close(fd)
        return path


def clean_temp_folder():
    for filename in os.listdir(TEMP):
        file_path = os.path.join(TEMP, filename)
        os.unlink(file_path)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        uploaded_file = request.FILES['file']
        temp_file = os.path.join(TEMP, uploaded_file.name)
        folder_id = get_folder_id_by_user(request.user)

        if form.is_valid():
            with open(temp_file, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            async_to_sync(upload_file_to_drive)(temp_file, uploaded_file.name, folder_id=folder_id)
            get_cache_data(request)
            os.remove(temp_file)
            return redirect('files:listfiles')
    else:
        form = UploadFileForm()
    return render(request, 'files/upload_form.html', {'form': form})


async def upload_file_to_drive(full_path, new_name, folder_id):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")

        req = drive_v3.files.create(
            upload_file=full_path,
            fields="id",
            json={"name": new_name,
                  "parents": [folder_id]})

        upload_res = await aiogoogle.as_user(req)
        print(f"folder id: {folder_id}")
        print("Uploaded {} successfully.\nFile ID: {}".format(full_path, upload_res['id']))


async def create_folder_on_drive(folder_name):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:

        drive_v3 = await aiogoogle.discover("drive", "v3")
        query = "name = '{}' and mimeType = 'application/vnd.google-apps.folder and trash = false'".format(folder_name)
        existing_folder = await aiogoogle.as_user(drive_v3.files.list(q=query))
        print(f"existing_folder: {existing_folder}")

        if existing_folder['files']:
            print(f'existing folder files:{existing_folder['files']}')
            print(f"return existing folder {existing_folder['files'][0]['id']}")
            return existing_folder['files'][0]['id']

        else:
            req = drive_v3.files.create(
                fields="id",
                json={"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            )

            # Execute the request
            folder_res = await aiogoogle.as_user(req)
            print(folder_res)
            print("Created folder successfully.\nFolder ID: {}".format(folder_res['id']))
            return folder_res['id']


async def delete_file(request, file_id, template_name):

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
        await aiogoogle.as_user(
            drive_v3.files.delete(fileId=file_id)
        )
    await sync_to_async(get_cache_data)(request)

    match template_name:
        case 'images':
            return_template = 'files:show_images'
        case 'documents':
            return_template = 'files:show_documents'
        case 'videos':
            return_template = 'files:show_videos'
        case 'other':
            return_template = 'files:show_other'
    print(template_name)
    return redirect(return_template)


def show_images(request):
    data = get_cache_data(request)
    return render(request, 'files/images.html', context={'images': data['images']})


def show_documents(request):
    data = get_cache_data(request)
    return render(request, 'files/documents.html', context={'documents': data['documents']})


def show_videos(request):
    data = get_cache_data(request)
    return render(request, 'files/videos.html', context={'videos': data['videos']})


def show_other(request):
    data = get_cache_data(request)
    return render(request, 'files/other.html', context={'other': data['other']})
