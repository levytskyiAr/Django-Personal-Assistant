import os
import mimetypes

from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import FileResponse
from aiogoogle import Aiogoogle
from asgiref.sync import async_to_sync, sync_to_async
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

from .async_google_drive.helpers import user_creds, client_creds
from .forms import UploadFileForm
from .models import UserFolderGoogleDrive

mimetypes.init()
TEMP = f'media/uploads/temp'


def get_cache_data(request):
    print('Data from cache')
    return cache.get(request.user.id)


def update_cache_data(request):
    data = async_to_sync(get_file_list_from_drive)(get_folder_id_by_user(request.user))
    cache.set(request.user.id, data, timeout=3600)
    print('Data from Google Drive')
    return data


def get_folder_id_by_user(user: User) -> str:
    """
    A function to get the folder id by user. Takes a User object as input and returns a string.
    """
    with transaction.atomic():
        write_to_db, created = UserFolderGoogleDrive.objects.get_or_create(user=user)
        if created:
            get_user = User.objects.get(id=user.id)
            folder_name_for_drive = f"id^{user.id}__username^{get_user.username}"
            folder_id = async_to_sync(create_folder_on_drive)(folder_name_for_drive)
            write_to_db.folder_drive_id = folder_id
            write_to_db.save()
        return write_to_db.folder_drive_id


@login_required
def get_filelist_from_drive(request):
    """
    A function that retrieves a file list from the cache for a specific user from the request object and renders it in a template.

    Parameters:
    - request: The request object containing user information

    Returns:
    - Renders a template with the file list data for documents, images, videos, and other file types, along with the user ID
    """
    clean_temp_folder()
    data = get_cache_data(request)
    if not data:
        data = update_cache_data(request)
    return render(request, 'files/base_for_files.html',
                  {'documents': data['documents'],
                   'images': data['images'], 'videos': data['videos'],
                   'other': data['other'], 'user_id': request.user.id
                   })


async def get_file_list_from_drive(folder_id):
    """
    Retrieves a list of files from Google Drive within a specified folder.
    Args:
        folder_id (str): The ID of the folder in Google Drive.

    Returns:
        dict: A dictionary containing categorized files with keys for documents, videos, images, and other files.
    """
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
    """
    Asynchronously opens a file and returns a FileResponse.
    Parameters:
        request: The request object.
        file_id: The ID of the file to open.
    Returns:
        FileResponse: The response containing the opened file.
    """
    path_to_temporary_file = await create_file_with_correct_name(file_id)
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_user(
        drive_v3.files.get(fileId=file_id, download_file=path_to_temporary_file, alt='media'), )

    return FileResponse(open(path_to_temporary_file, 'rb'))


async def download_file(request, file_id):
    """
    Download a file from Google Drive using the provided file ID.

    Args:
        request: The request object.
        file_id: The ID of the file to be downloaded.

    Returns:
        FileResponse: The response object containing the downloaded file.
    """
    path_to_temporary_file = await create_file_with_correct_name(file_id)
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_user(
        drive_v3.files.get(fileId=file_id, download_file=path_to_temporary_file, alt='media'), )

    return FileResponse(open(path_to_temporary_file, 'rb'), as_attachment=True)


async def create_file_with_correct_name(file_id):
    """
    A function that creates a file with a correct name based on the provided file ID.

    Parameters:
    file_id (str): The ID of the file to create.

    Returns:
    str: The path of the created file.
    """
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


@login_required
def upload_file(request):
    """
    A function to handle file uploads. It processes the uploaded file, saves it temporarily,
    validates the form, writes the file to disk, uploads it to a cloud drive asynchronously,
    retrieves cache data, and finally removes the temporary file.
    Parameters:
    - request: HttpRequest object containing the request data.
    Returns:
    - Redirects to 'files:listfiles' URL upon successful file uploads.
    - Renders the uploads form page with the form data for GET requests.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        uploaded_file = request.FILES['file']
        mime_type, encoding = mimetypes.guess_type(uploaded_file.name)
        temp_file = os.path.join(TEMP, uploaded_file.name)
        folder_id = get_folder_id_by_user(request.user)

        if form.is_valid():
            with open(temp_file, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            async_to_sync(upload_file_to_drive)(temp_file, uploaded_file.name, folder_id=folder_id)
            update_cache_data(request)
            os.remove(temp_file)
            return_template = choice_return_template(mime_type.split('/')[0])
            return redirect(return_template)
    else:
        form = UploadFileForm()
    return render(request, 'files/upload_form.html', {'form': form})


async def upload_file_to_drive(full_path, new_name, folder_id):
    """
    Uploads a file to Google Drive.

    Parameters:
    - full_path (str): The full path of the file to uploads.
    - new_name (str): The new name to assign to the uploaded file.
    - folder_id (str): The ID of the folder in Google Drive where the file will be uploaded.

    Returns:
    - None
    """
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")

        req = drive_v3.files.create(
            upload_file=full_path,
            fields="id",
            json={"name": new_name,
                  "parents": [folder_id]})

        upload_res = await aiogoogle.as_user(req)


async def create_folder_on_drive(folder_name):
    """
    A function to create a folder on Google Drive using the given folder name.

    Parameters:
    - folder_name: a string representing the name of the folder to be created on Google Drive

    Returns:
    - The ID of the newly created folder on Google Drive
    """
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:

        drive_v3 = await aiogoogle.discover("drive", "v3")
        query = "name = '{}' and mimeType = 'application/vnd.google-apps.folder and trash = false'".format(folder_name)
        existing_folder = await aiogoogle.as_user(drive_v3.files.list(q=query))

        if existing_folder['files']:
            return existing_folder['files'][0]['id']

        else:
            req = drive_v3.files.create(
                fields="id",
                json={"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            )

            # Execute the request
            folder_res = await aiogoogle.as_user(req)
            return folder_res['id']


async def delete_file(request, file_id):
    """
    A function to delete a file using the provided file_id and template_name.

    Parameters:
    - request: The request object.
    - file_id: The id of the file to be deleted.
    - template_name: The name of  the  template to determine the return_template.

    Returns:
    - Redirects to the appropriate return_template based on the template_name.
    """

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        drive_v3 = await aiogoogle.discover('drive', 'v3')
        await aiogoogle.as_user(
            drive_v3.files.delete(fileId=file_id)
        )
    await sync_to_async(update_cache_data)(request)
    return_template = choice_return_template(request.headers['Referer'].split('/')[-2])
    return redirect(return_template)


def choice_return_template(template_name):
    print(template_name)
    match template_name:
        case 'image' | 'images':
            return_template = 'files:show_images'

        case 'document' | 'text' | 'application' | 'documents':
            return_template = 'files:show_documents'

        case 'video' | 'videos':
            return_template = 'files:show_videos'

        case _:
            return_template = 'files:other'
    return return_template


@login_required
def show_images(request):
    """
    This function takes a request and retrieves data from the cache based on the request. It then renders an HTML template 'files/images.html' with a context containing the images data fetched from the cache.
    """
    data = get_cache_data(request)
    return render(request, 'files/images.html', context={'images': data['images']})


@login_required
def show_documents(request):
    """
    Retrieve data from cache based on request and render documents.html with   the retrieved data.
    :param request: The request object.
    :return: Rendered documents.html template with the documents context.
    """
    data = get_cache_data(request)
    return render(request, 'files/documents.html', context={'documents': data['documents']})


@login_required
def show_videos(request):
    """
    A function that shows videos based on the request data.

    Parameters:
    - request: The request object containing information needed to display videos.

    Returns:
    - A rendered HTML page displaying videos.
    """
    data = get_cache_data(request)
    return render(request, 'files/videos.html', context={'videos': data['videos']})


@login_required
def show_other(request):
    """
    Retrieve cache data and render the 'other.html' template with the 'other' data.

    Parameters:
        request: The request object.

    Returns:
        The rendered 'other.html' template with the 'other' data.
    """
    data = get_cache_data(request)
    return render(request, 'files/other.html', context={'other': data['other']})
