import os

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from aiogoogle import Aiogoogle
from asgiref.sync import sync_to_async, async_to_sync

from .async_google_drive.helpers import user_creds, client_creds
import aiogoogle
from .forms import UploadFileForm
from .models import UserFolderGoogleDrive


def get_filelist_from_drive(request):
    user_id = request.user.id
    folders = UserFolderGoogleDrive.objects.get(user=user_id)
    print(folders.folder_drive_id)
    # for folder in folders:
    #     print(folder.folder_drive_id, folder.user_id)
    # print(user_id)
    # try:
    #     user = User.objects.get(id=user_id)
    #     folder = UserFolderGoogleDrive.objects.get(user=user)
    #     print(folder)
    # except User.DoesNotExist:
    #     print(f"User with id {user_id} does not exist.")
    # except UserFolderGoogleDrive.DoesNotExist:
    #     print(f"Folder for user with id {user_id} does not exist.")

    documents, videos, images, other = async_to_sync(get_file_list_from_drive)(folders.folder_drive_id)
    return render(request, 'files/async_show_files_list.html', {
        'documents': documents,
        'videos': videos,
        'images': images,
        'other': other
    })


async def get_file_list_from_drive(folder_id):
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
    # return render(request, 'files/async_show_files_list.html', {
    #     'documents': documents,
    #     'videos': videos,
    #     'images': images,
    #     'other': other
    # })
    return documents, videos, images, other


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


async def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        uploaded_file = request.FILES['file']
        temp_folder = f'media/uploads/temp_upload/{uploaded_file.name}'
        # file_name = uploaded_file.name
        # file_mimetype = uploaded_file.content_type

        if form.is_valid():
            with open(temp_folder, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            await upload_file_to_drive(temp_folder, uploaded_file.name)
            # os.remove(temp_folder)
            return render(request, 'files/upload_success.html')
    else:
        form = UploadFileForm()
    return render(request, 'files/upload_form.html', {'form': form})


async def upload_file_to_drive(full_path, new_name):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        folder_id = await create_folder_on_drive("Id_user_name2")
        drive_v3 = await aiogoogle.discover("drive", "v3")

        req = drive_v3.files.create(
            upload_file=full_path,
            fields="id",
            json={"name": new_name,
                  "parents": [folder_id]}
        )

        # req.upload_file_content_type = mimetypes.guess_type(full_path)[0]

        # Upload file
        upload_res = await aiogoogle.as_user(req)
        print(f"folder id: {folder_id}")
        print("Uploaded {} successfully.\nFile ID: {}".format(full_path, upload_res['id']))
        # file_id = upload_res["id"]
        # # Rename uploaded file
        # await aiogoogle.as_user(
        #     drive_v3.files.update(fileId=file_id, json={"name": new_name})
        # )
        # print("Renamed {} to {} successfully!".format(full_path, new_name))


async def create_folder_on_drive(folder_name):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:

        drive_v3 = await aiogoogle.discover("drive", "v3")
        query = "name = '{}' and mimeType = 'application/vnd.google-apps.folder'".format(folder_name)
        existing_folders = await aiogoogle.as_user(drive_v3.files.list(q=query))
        print(f"existing_folders: {existing_folders}")

        if existing_folders['files']:
            print(f'existing folder files:{existing_folders['files']}')
            print(f"return existing folder {existing_folders['files'][0]['id']}")
            return existing_folders['files'][0]['id']

        else:
            req = drive_v3.files.create(
                fields="id",
                json={"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            )

            # Execute the request
            folder_res = await aiogoogle.as_user(req)
            print("Created folder successfully.\nFolder ID: {}".format(folder_res['id']))
            return folder_res['id']
